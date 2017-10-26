from formtools.wizard.views import SessionWizardView
from directory_constants.constants.exred_sector_names import CODES_SECTORS_DICT

from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django.views.generic import View

from article import structure
from triage import forms, helpers
from casestudy import casestudies


class CompaniesHouseSearchApiView(View):
    form_class = forms.CompaniesHouseSearchForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(data=request.GET)
        if not form.is_valid():
            return JsonResponse(form.errors, status=400)
        api_response = helpers.CompaniesHouseClient.search(
            term=form.cleaned_data['term']
        )
        api_response.raise_for_status()
        return JsonResponse(api_response.json()['items'], safe=False)


class TriageWizardFormView(SessionWizardView):

    SECTOR = 'SECTOR'
    EXPORTED_BEFORE = 'EXPORTED_BEFORE'
    REGULAR_EXPORTER = 'REGULAR_EXPORTER'
    ONLINE_MARKETPLACE = 'ONLINE_MARKETPLACE'
    COMPANY = 'COMPANY'
    SOLE_TRADER_CONFIRM = 'SOLE_TRADER_CONFIRM'
    SUMMARY = 'SUMMARY'

    form_list = (
        (SECTOR, forms.SectorForm),
        (EXPORTED_BEFORE, forms.ExportExperienceForm),
        (REGULAR_EXPORTER, forms.RegularExporterForm),
        (ONLINE_MARKETPLACE, forms.OnlineMarketplaceForm),
        (COMPANY, forms.CompanyForm),
        (SOLE_TRADER_CONFIRM, forms.SoleTraderForm),
        (SUMMARY, forms.EmptyForm),
    )
    templates = {
        SECTOR: 'triage/wizard-step-sector.html',
        EXPORTED_BEFORE: 'triage/wizard-step-exported-before.html',
        REGULAR_EXPORTER: 'triage/wizard-step-regular-exporter.html',
        ONLINE_MARKETPLACE: 'triage/wizard-step-online-marketplace.html',
        COMPANY: 'triage/wizard-step-company.html',
        SOLE_TRADER_CONFIRM: 'triage/wizard-step-sole-trader.html',
        SUMMARY: 'triage/wizard-step-summary.html',
    }
    success_url = reverse_lazy('custom-page')

    @cached_property
    def persisted_triage_answers(self):
        answer_manager = helpers.TriageAnswersManager(self.request)
        return answer_manager.retrieve_answers()

    def get_form_initial(self, step):
        return self.persisted_triage_answers

    def process_step(self, form):
        if self.is_user_skipping_current_step:
            return {}
        if self.steps.current == self.REGULAR_EXPORTER:
            is_regular = forms.get_is_regular_exporter(form.cleaned_data)
            self.condition_dict[self.ONLINE_MARKETPLACE] = not is_regular
        elif self.steps.current == self.EXPORTED_BEFORE:
            has_exported = forms.get_has_exported_before(form.cleaned_data)
            self.condition_dict[self.ONLINE_MARKETPLACE] = has_exported
            self.condition_dict[self.REGULAR_EXPORTER] = has_exported
        elif self.steps.current == self.COMPANY:
            is_found = forms.get_is_limited_company(form.cleaned_data)
            self.condition_dict[self.SOLE_TRADER_CONFIRM] = not is_found
        return super().process_step(form)

    def render_next_step(self, form):
        if self.steps.current == self.SOLE_TRADER_CONFIRM:
            if not forms.get_is_sole_trader(form.cleaned_data):
                return self.render_goto_step(self.COMPANY)
        if self.steps.current == self.COMPANY:
            if self.is_user_skipping_current_step:
                self.storage.set_step_data(self.COMPANY, {})
                self.storage.set_step_data(self.SOLE_TRADER_CONFIRM, {})
                return self.render_goto_step(self.SUMMARY)
        return super().render_next_step(form)

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    @property
    def is_user_reviewing_persisted_answers(self):
        # on the custom page there is a link to "change your preferences". That
        # link includes '?result' in the querystring. This indicates that the
        # user should be sent to the last step in the wizard to review their
        # answers
        return 'result' in self.request.GET

    @property
    def is_user_skipping_current_step(self):
        return 'wizard_skip_step' in self.request.POST

    def get_all_cleaned_data(self):
        # when updating answers the user can go from SUMMARY back to
        # COMPANY, then clicks forwards (without going all the way to the end)
        # meaning the steps not visited before COMPANY will not be present
        # in get_all_cleaned_data. Solve this by using persisted_triage_answers
        # and updating with get_all_cleaned_data
        return {
            **self.persisted_triage_answers,
            **super().get_all_cleaned_data()
        }

    def get(self, *args, **kwargs):
        if self.is_user_reviewing_persisted_answers:
            return self.render_goto_step(self.SUMMARY)
        return super().get(*args, **kwargs)

    def render_done(self, form, **kwargs):
        if self.is_user_reviewing_persisted_answers:
            return redirect(self.success_url)
        return super().render_done(form, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == self.SUMMARY:
            data = self.get_all_cleaned_data()
            context['all_cleaned_data'] = data
            context['sector_label'] = forms.get_sector_label(data)
            context['persona'] = forms.get_persona(data)
            context['is_user_reviewing_persisted_answers'] = (
                self.is_user_reviewing_persisted_answers
            )
        return context

    def done(self, *args, **kwargs):
        answers = forms.serialize_triage_form(self.get_all_cleaned_data())
        answer_manager = helpers.TriageAnswersManager(self.request)
        answer_manager.persist_answers(answers)
        return redirect(self.success_url)


class CustomPageView(TemplateView):
    http_method_names = ['get']
    template_name = 'triage/custom-page.html'

    @cached_property
    def triage_answers(self):
        answer_manager = helpers.TriageAnswersManager(self.request)
        return answer_manager.retrieve_answers()

    def dispatch(self, request, *args, **kwargs):
        if not self.triage_answers:
            return redirect('triage-wizard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona'] = forms.get_persona(self.triage_answers)
        context['triage_result'] = self.triage_answers
        context['section_configuration'] = self.get_section_configuration()
        context['casestudies'] = [
            casestudies.MARKETPLACE,
            casestudies.HELLO_BABY,
            casestudies.YORK,
        ]
        sector_code = self.triage_answers['sector']
        # harmonised system codes begin with HS. Service codes begin with EB
        if sector_code.startswith('HS'):
            context['top_markets'] = helpers.get_top_markets(sector_code)
            context['sector_name'] = CODES_SECTORS_DICT[sector_code]
            context['top_importer'] = helpers.get_top_importer(sector_code)
        return context

    def get_section_configuration(self):
        answers = self.triage_answers
        persona = forms.get_persona(answers)
        if persona == forms.NEW_EXPORTER:
            return self.get_persona_new_section_configuration(answers)
        elif persona == forms.OCCASIONAL_EXPORTER:
            return self.get_persona_occasional_section_configuration(answers)
        elif persona == forms.REGULAR_EXPORTER:
            return self.get_persona_regular_section_configuration(answers)

    @staticmethod
    def get_persona_new_section_configuration(answers):
        return {
            'persona_article_group': structure.PERSONA_NEW_ARTICLES,
            'trade_profile': not forms.get_is_sole_trader(answers),
            'selling_online_overseas': False,
            'selling_online_overseas_and_export_opportunities': False,
            'articles_resources': False,
            'case_studies': True,
        }

    @staticmethod
    def get_persona_occasional_section_configuration(answers):
        return {
            'persona_article_group': structure.PERSONA_OCCASIONAL_ARTICLES,
            'trade_profile': not forms.get_is_sole_trader(answers),
            'selling_online_overseas': forms.get_used_marketplace(answers),
            'selling_online_overseas_and_export_opportunities': False,
            'articles_resources': False,
            'case_studies': True,
        }

    @staticmethod
    def get_persona_regular_section_configuration(answers):
        return {
            'persona_article_group': [],
            'trade_profile': not forms.get_is_sole_trader(answers),
            'selling_online_overseas': False,
            'selling_online_overseas_and_export_opportunities': True,
            'articles_resources': True,
            'case_studies': False,
        }
