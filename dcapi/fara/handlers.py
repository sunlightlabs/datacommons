from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, ComparisonField, FulltextField
from dcapi.schema import Schema, FunctionField, Field
from dcdata.fara.models import ClientRegistrant, Contact, Contribution, Disbursement, Payment
from dcdata.utils.sql import parse_date
from dcapi.contributions.transaction_types import transaction_type_descriptions
from decimal import Decimal


#
# CLIENT REGISTRANT
#

def _terminated_generator(query, terminated_active):
    return query.filter(terminated=terminated_active.title())

CLIENT_REGISTRANT_SCHEMA = Schema(
    FunctionField('terminated', _terminated_generator),
    InclusionField('registrant_id'),
    InclusionField('client_id'),
    InclusionField('location_id'),
    FulltextField('client_ft', ['client',]),
    FulltextField('registrant_name_ft', ['registrant_name',]),
    FulltextField('location_of_client_ft', ['location_of_client',]),
    FulltextField('description_of_service_ft', ['description_of_service',]),
)

def filter_client_registrant(request):
    return CLIENT_REGISTRANT_SCHEMA.build_filter(ClientRegistrant.objects, request).order_by()

CLIENT_REGISTRANT_FIELDS = list(ClientRegistrant.FIELDNAMES)

class ClientRegistrantFilterHandler(FilterHandler):
    fields = ClientRegistrant.FIELDNAMES
    model = ClientRegistrant
    ordering = ['client',]
    filename = 'fara_client_registrant'
    
    def queryset(self, params):
        return filter_client_registrant(self._unquote(params))

    def read(self, request):
        return super(ClientRegistrantFilterHandler, self).read(request)

#
# CONTACT 
#

CONTACT_SCHEMA = Schema(
    ComparisonField('date', cast=parse_date),
    InclusionField('contact_type'),
    InclusionField('affiliated_memember_bioguide_id'),
    InclusionField('document_id'),
    InclusionField('registrant_id'),
    InclusionField('client_id'),
    InclusionField('location_id'),
    InclusionField('recipient_id'),
    InclusionField('record_id'),
    FulltextField('contact_title_ft', ['contact_title',]),
    FulltextField('contact_name_ft', ['contact_name',]),
    FulltextField('contact_office_ft', ['contact_office',]),
    FulltextField('contact_agency_ft', ['contact_agency',]),
    FulltextField('client_ft', ['client',]),
    FulltextField('client_location_ft', ['client_location',]),
    FulltextField('registrant_ft', ['registrant',]),
    FulltextField('description_ft', ['description',]),
    FulltextField('employees_mentioned_ft', ['employees_mentioned',]),
)

def filter_contacts(request):
    return CONTACT_SCHEMA.build_filter(Contact.objects, request).order_by()

CONTACT_FIELDS = list(Contact.FIELDNAMES)

class ContactFilterHandler(FilterHandler):
    fields = Contact.FIELDNAMES
    model = Contact
    ordering = ['-date',]
    filename = 'fara_contacts'
    
    def queryset(self, params):
        return filter_contacts(self._unquote(params))

    def read(self, request):
        return super(ContactFilterHandler, self).read(request)


#
# CONTRIBUTION
#

CONTRIBUTION_SCHEMA = Schema(
    ComparisonField('date', cast=parse_date),
    ComparisonField('amount', cast=Decimal),
    InclusionField('contact_type'),
    InclusionField('document_id'),
    InclusionField('recipient_crp_id'),
    InclusionField('recipient_bioguide_id'),
    InclusionField('registrant_id'),
    InclusionField('recipient_id'),
    InclusionField('record_id'),
    FulltextField('recipient_ft', ['recipient',]),
    FulltextField('description_ft', ['description',]),
    FulltextField('contributing_individual_or_pac_ft', ['contributing_individual_or_pac',]),
)

def filter_contributions(request):
    return CONTRIBUTION_SCHEMA.build_filter(Contribution.objects, request).order_by()

CONTRIBUTION_FIELDS = list(Contribution.FIELDNAMES)

class ContributionFilterHandler(FilterHandler):
    fields = Contribution.FIELDNAMES
    model = Contribution
    ordering = ['-date',]
    filename = 'fara_contributions'
    
    def queryset(self, params):
        return filter_contributions(self._unquote(params))

    def read(self, request):
        return super(ContributionFilterHandler, self).read(request)


#
# DISBURSEMENT 
#

DISBURSEMENT_SCHEMA = Schema(
    ComparisonField('date', cast=parse_date),
    ComparisonField('amount', cast=Decimal),
    InclusionField('document_id'),
    InclusionField('registrant_id'),
    InclusionField('client_id'),
    InclusionField('location_id'),
    InclusionField('subcontractor_id'),
    InclusionField('record_id'), 
    FulltextField('client_ft', ['client',]),
    FulltextField('registrant_ft', ['registrant',]),
    FulltextField('purpose_ft', ['purpose',]),
    FulltextField('to_subcontractor_ft', ['to_subcontractor',])
)

def filter_disbursements(request):
    return DISBURSEMENT_SCHEMA.build_filter(Disbursement.objects, request).order_by()

DISBURSEMENT_FIELDS = list(Disbursement.FIELDNAMES)

class DisbursementFilterHandler(FilterHandler):
    fields = Disbursement.FIELDNAMES
    model = Disbursement
    ordering = ['-date',]
    filename = 'fara_disbursements'
    
    def queryset(self, params):
        return filter_disbursements(self._unquote(params))

    def read(self, request):
        return super(DisbursementFilterHandler, self).read(request)


#
# PAYMENT 
#

PAYMENT_SCHEMA = Schema(
    ComparisonField('date', cast=parse_date),
    ComparisonField('amount', cast=Decimal),
    InclusionField('document_id'),
    InclusionField('registrant_id'),
    InclusionField('client_id'),
    InclusionField('location_id'),
    InclusionField('subcontractor_id'),
    InclusionField('record_id'), 
    FulltextField('client_ft', ['client',]),
    FulltextField('registrant_ft', ['registrant',]),
    FulltextField('purpose_ft', ['purpose',]),
    FulltextField('from_subcontractor_ft', ['to_subcontractor',])
)

def filter_contributions(request):
    return PAYMENT_SCHEMA.build_filter(Payment.objects, request).order_by()

PAYMENT_FIELDS = list(Payment.FIELDNAMES)

class PaymentFilterHandler(FilterHandler):
    fields = Payment.FIELDNAMES
    model = Payment
    ordering = ['-date',]
    filename = 'fara_payments'
    
    def queryset(self, params):
        return filter_disbursements(self._unquote(params))

    def read(self, request):
        return super(PaymentFilterHandler, self).read(request)


