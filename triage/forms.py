from collections import namedtuple

from directory_constants.constants import exred_sector_names

from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH

from core.widgets import RadioSelect
from triage import fields


Persona = namedtuple('Persona', ['key', 'label'])
REGULAR_EXPORTER = Persona(key='REGULAR_EXPORTER', label='Regular Exporter')
OCCASIONAL_EXPORTER = Persona(
    key='OCCASIONAL_EXPORTER', label='Occasional Exporter'
)
NEW_EXPORTER = Persona(key='NEW_EXPORTER', label='New Exporter')


class BaseTriageForm(forms.Form):
    use_required_attribute = False
    error_css_class = 'input-field-container has-error'


class SectorForm(BaseTriageForm):
    sector = forms.ChoiceField(
        choices=BLANK_CHOICE_DASH + list(exred_sector_names.SECTORS_CHOICES),
        label='What is your sector?',
        label_suffix='',
        widget=forms.Select(attrs={'id': 'js-sector-select'}),
    )


class ExportExperienceForm(BaseTriageForm):
    exported_before = forms.TypedChoiceField(
        label='Have you exported before?',
        label_suffix='',
        coerce=lambda x: x == 'True',
        choices=[(True, 'Yes'), (False, 'No')],
        widget=RadioSelect()
    )


class RegularExporterForm(BaseTriageForm):
    regular_exporter = forms.TypedChoiceField(
        label='Is exporting a regular part of your business?',
        label_suffix='',
        coerce=lambda x: x == 'True',
        choices=[(True, 'Yes'), (False, 'No')],
        widget=RadioSelect(),
    )


class OnlineMarketplaceForm(BaseTriageForm):
    used_online_marketplace = forms.TypedChoiceField(
        label='Do you use online marketplace to sell your products?',
        label_suffix='',
        coerce=lambda x: x == 'True',
        choices=[(True, 'Yes'), (False, 'No')],
        widget=RadioSelect()
    )


class CompanyForm(BaseTriageForm):
    company_name = forms.CharField(
        label='What is your company name? (optional)',
        help_text="We'll use this information to personalise your experience",
        label_suffix='',
        max_length=1000,
        required=False,
        widget=forms.TextInput(
            attrs={'id': 'js-typeahead-company-name'}
        ),
    )
    company_number = fields.PaddedCharField(
        label='Company number:',
        max_length=8,
        fillchar='0',
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'js-typeahead-company-number'}),
    )


class SoleTraderForm(BaseTriageForm):
    sole_trader = forms.TypedChoiceField(
        label='We could not find your company name. Are you a sole trader?',
        label_suffix='',
        coerce=lambda x: x == 'True',
        choices=[(True, 'Yes'), (False, 'No, enter company name again')],
        widget=RadioSelect(),
        required=False,
        initial=False,
    )

    def clean_sole_trader(self):
        return (
            self.cleaned_data['sole_trader'] or
            self.fields['sole_trader'].initial
        )


class EmptyForm(forms.Form):
    pass


class CompaniesHouseSearchForm(forms.Form):
    term = forms.CharField()


def get_persona(cleaned_data):
    is_regular_exporter = cleaned_data.get('regular_exporter') is True
    has_exported_before = cleaned_data.get('exported_before') is True

    if is_regular_exporter:
        return REGULAR_EXPORTER
    elif not is_regular_exporter and has_exported_before:
        return OCCASIONAL_EXPORTER
    return NEW_EXPORTER


def get_has_exported_before(answers):
    return answers.get('exported_before') is True


def get_is_regular_exporter(answers):
    return answers.get('regular_exporter') is True


def get_is_sole_trader(answers):
    return answers.get('sole_trader') is True


def get_is_limited_company(answers):
    return answers.get('company_number') != ''


def get_used_marketplace(answers):
    return answers.get('used_online_marketplace') is True


def get_sector_label(cleaned_data):
    for key, label in exred_sector_names.SECTORS_CHOICES:
        if key == cleaned_data['sector']:
            return label


def serialize_triage_form(data):
    return {
        'sector': data['sector'],
        'exported_before': data['exported_before'],
        'regular_exporter': data.get('regular_exporter') or False,
        'used_online_marketplace': data.get('used_online_marketplace'),
        'company_name': data.get('company_name', ''),
        'sole_trader': data.get('sole_trader') or False,
        'company_number': data.get('company_number', ''),
    }
