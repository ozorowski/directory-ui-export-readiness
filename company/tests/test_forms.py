from unittest.mock import Mock

from django.forms.fields import Field

from company.forms import shared_enrolment_validators, shared_validators
from directory_validators.constants import choices

from company import forms

from enrolment.forms import AutoFocusFieldMixin, IndentedInvalidFieldsMixin

from django.core.validators import URLValidator

URL_FORMAT_MESSAGE = URLValidator.message
REQUIRED_MESSAGE = Field.default_error_messages['required']


def create_mock_file():
    return Mock(size=1)


def test_serialize_supplier_case_study_forms():
    data = {
        'title': 'a title',
        'description': 'a description',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'year': '2010',
        'keywords': 'goog, great',
        'image_one': '1.png',
        'image_two': '2.png',
        'image_three': '3.png',
        'testimonial': 'very nice',
    }
    expected = {
        'title': 'a title',
        'description': 'a description',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'year': '2010',
        'keywords': 'goog, great',
        'image_one': '1.png',
        'image_two': '2.png',
        'image_three': '3.png',
        'testimonial': 'very nice',
    }

    actual = forms.serialize_supplier_case_study_forms(data)

    assert actual == expected


def test_case_study_basic_info_validators():
    field = forms.CaseStudyBasicInfoForm.base_fields['keywords']
    assert shared_validators.keywords_word_limit in field.validators


def test_case_study_form_required_fields():
    form = forms.CaseStudyBasicInfoForm(data={})

    assert form.is_valid() is False
    assert form.errors['title'] == [REQUIRED_MESSAGE]
    assert form.errors['description'] == [REQUIRED_MESSAGE]
    assert form.errors['sector'] == [REQUIRED_MESSAGE]
    assert form.errors['year'] == [REQUIRED_MESSAGE]
    assert form.errors['keywords'] == [REQUIRED_MESSAGE]


def test_case_study_form_all_fields():
    data = {
        'title': 'a title',
        'description': 'a description',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'year': '2010',
        'keywords': 'goog, great',
    }
    form = forms.CaseStudyBasicInfoForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data == data


def test_auto_focus_mixin_installed():
    FormClasses = [
        forms.CaseStudyBasicInfoForm,
        forms.CaseStudyRichMediaForm,
        forms.CompanyAddressVerificationForm,
        forms.CompanyBasicInfoForm,
        forms.CompanyClassificationForm,
        forms.CompanyContactDetailsForm,
        forms.CompanyDescriptionForm,
        forms.CompanyLogoForm,
        forms.PublicProfileSearchForm,
    ]
    for FormClass in FormClasses:
        assert issubclass(FormClass, AutoFocusFieldMixin)


def test_indent_invalid_mixin_installed():
    FormClasses = [
        forms.CaseStudyBasicInfoForm,
        forms.CaseStudyRichMediaForm,
        forms.CompanyAddressVerificationForm,
        forms.CompanyBasicInfoForm,
        forms.CompanyClassificationForm,
        forms.CompanyContactDetailsForm,
        forms.CompanyDescriptionForm,
        forms.CompanyLogoForm,
        forms.PublicProfileSearchForm,
    ]
    for FormClass in FormClasses:
        assert issubclass(FormClass, IndentedInvalidFieldsMixin)


def test_public_profile_search_form_default_page():
    data = {
        'sectors': choices.COMPANY_CLASSIFICATIONS[1][0]
    }
    form = forms.PublicProfileSearchForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data['page'] == 1


def test_public_profile_search_form_specified_page():
    data = {
        'sectors': choices.COMPANY_CLASSIFICATIONS[1][0],
        'page': 3
    }
    form = forms.PublicProfileSearchForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data['page'] == 3


def test_public_profile_search_form_requires_sectors():
    data = {}
    form = forms.PublicProfileSearchForm(data=data)

    assert form.is_valid() is False
    assert form.errors['sectors'] == [REQUIRED_MESSAGE]


def test_public_profile_search_form_valid_data():
    data = {
        'sectors': choices.COMPANY_CLASSIFICATIONS[1][0],
    }
    form = forms.PublicProfileSearchForm(data=data)

    assert form.is_valid() is True


def test_company_logo_form_accepts_valid_data():
    logo = create_mock_file()
    form = forms.CompanyLogoForm(files={'logo': logo})

    valid = form.is_valid()

    assert valid is True
    assert form.cleaned_data == {
        'logo': logo,
    }


def test_company_logo_form_logo_is_required():
    form = forms.CompanyLogoForm(files={'logo': None})

    valid = form.is_valid()

    assert valid is False
    assert 'logo' in form.errors
    assert 'This field is required.' in form.errors['logo']


def test_company_profile_logo_validator():
    field = forms.CompanyLogoForm.base_fields['logo']
    assert shared_enrolment_validators.logo_filesize in field.validators


def test_company_description_form_accepts_valid_data():
    form = forms.CompanyDescriptionForm(data={
        'description': 'thing'
    })
    assert form.is_valid() is True
    assert form.cleaned_data['description'] == 'thing'


def test_company_description_form_rejects_invalid_data():
    form = forms.CompanyDescriptionForm(data={})
    assert form.is_valid() is False
    assert form.errors['description'] == [REQUIRED_MESSAGE]


def test_company_profile_form_required_fields():
    form = forms.CompanyBasicInfoForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert form.errors['name'] == [REQUIRED_MESSAGE]
    assert form.errors['website'] == [REQUIRED_MESSAGE]
    assert form.errors['keywords'] == [REQUIRED_MESSAGE]


def test_company_profile_form_keywords_validator():
    field = forms.CompanyBasicInfoForm.base_fields['keywords']
    assert shared_validators.keywords_word_limit in field.validators


def test_company_profile_form_url_validator():
    field = forms.CompanyBasicInfoForm.base_fields['website']
    assert isinstance(field.validators[0], URLValidator)


def test_company_classification_form_sectors_validator():
    field = forms.CompanyClassificationForm.base_fields['sectors']
    assert shared_validators.sector_choice_limit in field.validators


def test_company_profile_form_accepts_valid_data():
    data = {
        'name': 'Amazon UK',
        'website': 'http://amazon.co.uk',
        'keywords': 'Ecommerce',
        'employees': '1-10',
    }
    form = forms.CompanyBasicInfoForm(data=data)

    valid = form.is_valid()

    assert valid is True
    assert form.cleaned_data == {
        'name': 'Amazon UK',
        'website': 'http://amazon.co.uk',
        'keywords': 'Ecommerce',
        'employees': '1-10',
    }


def test_serialize_company_profile_forms():

    actual = forms.serialize_company_profile_forms({
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'country': 'GB',
        'email_address': 'Jeremy@example.com',
        'email_full_name': 'Jeremy email',
        'employees': '1-10',
        'keywords': 'Jolly good exporter.',
        'locality': 'London',
        'name': 'Example ltd.',
        'po_box': '124',
        'postal_code': 'E14 9IX',
        'postal_full_name': 'Jeremy postal',
        'sectors': ['1', '2'],
        'website': 'http://example.com',
    })
    expected = {
        'keywords': 'Jolly good exporter.',
        'employees': '1-10',
        'name': 'Example ltd.',
        'sectors': ['1', '2'],
        'website': 'http://example.com',
        'contact_details': {
            'address_line_1': '123 Fake Street',
            'address_line_2': 'Fakeville',
            'country': 'GB',
            'email_address': 'Jeremy@example.com',
            'email_full_name': 'Jeremy email',
            'locality': 'London',
            'po_box': '124',
            'postal_code': 'E14 9IX',
            'postal_full_name': 'Jeremy postal',
        }
    }
    assert actual == expected


def test_serialize_company_logo_forms():
    logo = create_mock_file()
    actual = forms.serialize_company_logo_forms({
        'logo': logo,
    })
    expected = {
        'logo': logo,
    }
    assert actual == expected


def test_serialize_company_description_forms():
    actual = forms.serialize_company_description_forms({
        'description': 'Jolly good exporter.',
    })
    expected = {
        'description': 'Jolly good exporter.',
    }
    assert actual == expected


def test_company_contact_details_rejects_invalid():
    form = forms.CompanyContactDetailsForm(data={})

    assert form.is_valid() is False
    assert form.errors['email_address'] == [REQUIRED_MESSAGE]
    assert form.errors['email_full_name'] == [REQUIRED_MESSAGE]


def test_company_contact_details_accepts_valid():
    data = {
        'email_address': 'Jeremy@exmaple.com',
        'email_full_name': 'Jeremy',
    }
    form = forms.CompanyContactDetailsForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data == data


def test_company_address_verification_rejects_invalid():
    form = forms.CompanyAddressVerificationForm(data={})

    assert form.is_valid() is False
    assert form.errors['address_line_1'] == [REQUIRED_MESSAGE]
    assert form.errors['postal_code'] == [REQUIRED_MESSAGE]

    assert 'postal_full_name' not in form.errors
    assert 'address_line_2' not in form.errors
    assert 'locality' not in form.errors
    assert 'po_box' not in form.errors
    assert 'country' not in form.errors


def test_company_address_verification_accepts_valid():
    data = {
        'postal_full_name': 'Peter',
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'locality': 'London',
        'postal_code': 'E14 8UX',
        'po_box': '123',
        'country': 'GB',
    }
    form = forms.CompanyAddressVerificationForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data == data
