from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, FulltextField, ComparisonField
from dcapi.schema import Schema
from dcdata.contracts.models import Contract
from dcdata.utils.sql import parse_date


CONTRACTS_SCHEMA = Schema(
    InclusionField('agency_id', 'agencyid'),
    InclusionField('contracting_agency_id', 'contractingofficeagencyid'),
    InclusionField('fiscal_year'),
    InclusionField('place_district', 'congressionaldistrict'),
    InclusionField('place_state', 'statecode'),
    InclusionField('requesting_agency_id', 'fundingrequestingagencyid'),
    InclusionField('vendor_state', 'state'),
    InclusionField('vendor_zipcode', 'zipcode'),
    InclusionField('vendor_district', 'vendor_cd'),
    InclusionField('vendor_duns', 'dunsnumber'),
    InclusionField('vendor_parent_duns', 'eeparentduns'),

    # agency names have no data. see ticket #835
    #FulltextField('agency_name', ['agency_name', 'contracting_agency_name', 'requesting_agency_name']),
    FulltextField('vendor_name', ['vendorname']),
    FulltextField('vendor_city', ['city']),

    ComparisonField('obligated_amount', 'obligatedamount', cast=int),
    ComparisonField('current_amount', 'baseandexercisedoptionsvalue', cast=int),
    ComparisonField('maximum_amount', 'baseandalloptionsvalue', cast=int),
    ComparisonField('signed_date', 'signeddate', cast=parse_date),
)


def filter_contracts(request):
    return CONTRACTS_SCHEMA.build_filter(Contract.objects, request).order_by()


class ContractsFilterHandler(FilterHandler):

    # imported_on is marked as an auto-generated field/non-editable,
    # so was getting dropped by Django's model_to_dict serialization,
    # but still required by the list of fields,
    # so we pass the list of fields we want directly instead

    fields = Contract._meta.get_all_field_names()
    fields.remove('imported_on')


    ordering = ['-fiscal_year','-obligatedamount']
    filename = 'contracts'
        
    def queryset(self, params):
        return filter_contracts(self._unquote(params))
    
