from django.contrib.localflavor.us.models import USStateField
from django.db import models
from dcdata.models import Import
from dcdata.contracts import *

class Contract(models.Model):
    import_reference = models.ForeignKey(Import)
    
    id = models.BigIntegerField(primary_key=True, unique=True) # record_id
    transaction_number = models.IntegerField(blank=True, null=True) # transactionNumber, key + transactionNumber is unique
    
    fiscal_year = models.IntegerField() # fiscal_year
    version = models.CharField(max_length=10, blank=True, null=True) # version
    last_modified_date = models.DateTimeField(blank=True, null=True) # lastModifiedDate
    piid = models.CharField(max_length=50, blank=True, null=True) # piid
    
    parent_id = models.BigIntegerField(blank=True, null=True) # parent_id
    award_id = models.BigIntegerField(blank=True, null=True) # award_id
    
    modification_number = models.CharField(max_length=25, blank=True, null=True) # modNumber
    modification_reason = models.CharField(max_length=1, choices=MOD_REASONS, blank=True, null=True) # reasonForModification
    
    # agencies involved
    agency_name = models.CharField(max_length=255, blank=True, null=True) # <------------------------------
    agency_id = models.CharField(max_length=4, blank=True, null=True) # agencyID
    contracting_agency_name = models.CharField(max_length=255, blank=True, null=True) # <------------------------------
    contracting_agency_id = models.CharField(max_length=4, blank=True, null=True) # contractingOfficeAgencyID, FIPS code for office executing contract
    contracting_office_id = models.CharField(max_length=6, blank=True, null=True) # contractingOfficeID, agency assigned office ID
    requesting_agency_name = models.CharField(max_length=255, blank=True, null=True) # <------------------------------
    requesting_agency_id = models.CharField(max_length=4, blank=True, null=True) # fundingRequestingAgencyID
    requesting_office_id = models.CharField(max_length=6, blank=True, null=True) # fundingRequestingOfficeID
    major_program_code = models.CharField(max_length=100, blank=True, null=True) # majorProgramCode
    #idv_id = #######
    idv_agency_fee = models.DecimalField(default=0, max_digits=20, decimal_places=2, blank=True, null=True) # feePaidForUseOfService
    
    # contract information
    cotr_name = models.CharField(max_length=255, blank=True, null=True) # COTRName
    cotr_other_name = models.CharField(max_length=255, blank=True, null=True) # alternateCOTRName
    contract_action_type = models.CharField(max_length=1, choices=ACTION_TYPES, blank=True, null=True) # contractActionType
    contract_bundling_type = models.CharField(max_length=1, choices=BUNDLING, blank=True, null=True) # contractBundling
    contract_competitiveness = models.CharField(max_length=3, choices=COMPETITIVENESS, blank=True, null=True) # extentCompeted
    contract_description = models.TextField(blank=True, null=True) # descriptionOfContractRequirement
    contract_financing = models.CharField(max_length=1, choices=FINANCING, blank=True, null=True) # contractFinancing
    contract_nia_code = models.CharField(max_length=4, choices=NIA_CODES, blank=True, null=True) # nationalInterestActionCode
    contract_nocompete_reason = models.CharField(max_length=3, choices=NOCOMPETE_REASONS, blank=True, null=True) # reasonNotCompeted
    contract_offers_received = models.IntegerField(blank=True, null=True) # numberOfOffersReceived
    contract_pricing_type = models.CharField(max_length=1, choices=PRICING_TYPES, blank=True, null=True) # typeOfContractPricing
    contract_set_aside = models.CharField(max_length=10, choices=SET_ASIDES, blank=True, null=True) # typeOfSetAside
    subcontract_plan = models.CharField(max_length=1, choices=SUBCONTRACT_PLANS, blank=True, null=True) # subcontractPlan
    number_of_actions = models.IntegerField(blank=True, null=True) # numberOfActions
    consolidated_contract = models.NullBooleanField(blank=True, null=True) # consolidatedContract
    multiyear_contract = models.NullBooleanField(blank=True, null=True) # multiYearContract
    performance_based_contract = models.CharField(max_length=1, choices=YNX, blank=True, null=True) # performanceBasedServiceContract
    
    # dates
    signed_date = models.DateField(blank=True, null=True) # signedDate, date signed
    effective_date = models.DateField(blank=True, null=True) # effectiveDate, starting date
    completion_date = models.DateField(blank=True, null=True) # currentCompletionDate, ending date
    maximum_date = models.DateField(blank=True, null=True) #ultimateCompletionDate, max completion date if all options
    renewal_date = models.DateField(blank=True, null=True) # renewalDate
    cancellation_date = models.DateField(blank=True, null=True) # cancellationDate
    
    # amounts
    obligated_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, blank=True, null=True) # obligatedAmount
    current_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, blank=True, null=True) # baseAndExercisedOptionsValue
    maximum_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, blank=True, null=True) # baseAndAllOptionsValue
    price_difference = models.CharField(max_length=2, blank=True, null=True) # priceEvaluationPercentDifference
    cost_data_obtained = models.CharField(max_length=1, choices=COST_OBTAINED, blank=True, null=True) # costOrPricingData
    purchase_card_as_payment = models.NullBooleanField(blank=True, null=True) # purchaseCardAsPaymentMethod
    
    # vendor
    vendor_name = models.CharField(max_length=255, blank=True, null=True) # vendorName
    vendor_business_name = models.CharField(max_length=255, blank=True, null=True) # vendorDoingAsBusinessName
    vendor_employees = models.IntegerField(blank=True, null=True) # numberOfEmployees
    vendor_annual_revenue = models.DecimalField(default=0, max_digits=20, decimal_places=2, blank=True, null=True) # annualRevenue
    vendor_street_address = models.CharField(max_length=255, blank=True, null=True) # streetAddress
    vendor_street_address2 = models.CharField(max_length=255, blank=True, null=True) # streetAddress2
    vendor_street_address3 = models.CharField(max_length=255, blank=True, null=True) # streetAddress3
    vendor_city = models.CharField(max_length=35, blank=True, null=True) # city
    vendor_state = USStateField(blank=True, null=True) # state
    vendor_zipcode = models.CharField(max_length=10, blank=True, null=True) # ZIPCode
    vendor_district = models.CharField(max_length=4, blank=True, null=True) # vendor_cd
    vendor_country_code = models.CharField(max_length=3, blank=True, null=True) # vendorCountryCode, FIPS code
    vendor_duns = models.CharField(max_length=16, blank=True, null=True) # DUNSNumber
    vendor_parent_duns = models.CharField(max_length=9, blank=True, null=True) # parentDUNSNumber
    vender_phone = models.CharField(max_length=20, blank=True, null=True) # phoneNo
    vendor_fax = models.CharField(max_length=20, blank=True, null=True) # faxNo
    vendor_ccr_exception = models.CharField(max_length=1, choices=CCR_EXCEPTIONS, blank=True, null=True) # CCRException
    
    # place and product
    place_district = models.CharField(max_length=2, blank=True, null=True) # congressionalDistrict
    place_location_code = models.CharField(max_length=9, blank=True, null=True) # locationCode
    place_state_code = models.CharField(max_length=9, blank=True, null=True) # stateCode
    product_origin_country = models.CharField(max_length=2, blank=True, null=True) # countryOfOrigin, FIPS code
    product_origin = models.CharField(max_length=1, choices=PRODUCT_ORIGIN, blank=True, null=True) # placeOfManufacture
    producer_type = models.CharField(max_length=1, choices=ORG_TYPES, blank=True, null=True) # manufacturingOrganizationType
    
    # random fields
    statutory_authority = models.TextField(blank=True, null=True) # otherStatutoryAuthority
    product_service_code = models.CharField(max_length=4, blank=True, null=True) # productOrServiceCode
    naics_code = models.CharField(max_length=6, blank=True, null=True) # principalNAICSCode
    solicitation_id = models.CharField(max_length=100, blank=True, null=True) # solicitationID    
    supports_goodness = models.NullBooleanField(blank=True, null=True) # contingencyHumanitarianPeacekeepingOperation, "A designator of contract actions that support a declared contingency operation, a declared humanitarian operation or a declared peacekeeping operation."    
    dod_system_code = models.CharField(max_length=4, blank=True, null=True) # systemEquipmentCode
    it_commercial_availability = models.CharField(max_length=1, choices=COMMERCIAL, blank=True, null=True) # informationTechnologyCommercialItemCategory
    cas_clause = models.CharField(max_length=1, choices=YNX, blank=True, null=True) # costAccountingStandardsClause
    recovered_material_clause = models.CharField(max_length=1, choices=RM_CLAUSES, blank=True, null=True) # recoveredMaterialClauses
    fed_biz_opps = models.CharField(max_length=1, choices=YNX, blank=True, null=True) # fedBizOpps
    government_property = models.NullBooleanField(blank=True, null=True) # GFE_GFP
    
    class Meta:
        ordering = ('-id',)
    
    def __unicode__(self):
        return u"%s %s" % (self.fiscal_year, self.contract_description)
    
    
    """
    'organizationCode','contractFundCode','isPhysicallyComplete',
    'divisionName','divisionNumberOrOfficeCode','organizationalType'
    """
    
    ########### DEPRECATED
    #purchaseReason
    #contractorName
    #placeOfPerformanceCountryCode
    #placeOfPerformanceZIPCode
    #placeOfPerformanceCongressionalDistrict
    #reasonNotAwardedToSmallBusiness
    
    ########### no docs
    #createdBy
    #createdDate
    #lastModifiedBy
    #status
    #agencyspecificID
    #offerorsProposalNumber
    #PRNumber
    #closeoutPR
    #procurementPlacementCode
    #solicitationIssueDate
    #contractAdministrationDelegated
    #advisoryOrAssistanceServicesContract
    #supportServicesTypeContract
    #newTechnologyOrPatentRightsClause
    #managementReportingRequirements
    #propertyFinancialReporting
    #valueEngineeringClause
    #securityCode
    #administratorCode
    #contractingOfficerCode
    #negotiatorCode
    #physicalCompletionDate
    #installationUnique
    #fundedThroughDate
    #principalInvestigatorFirstName
    #principalInvestigatorMiddleInitial
    #principalInvestigatorLastName
    #alternatePrincipalInvestigatorFirstName
    #alternatePrincipalInvestigatorMiddleInitial
    #alternatePrincipalInvestigatorLastName
    #fieldOfScienceOrEngineering
    #finalInvoicePaidDate
    #accessionNumber
    #destroyDate
    #accountingInstallationNumber
    #wildFireProgram
    #eeParentDuns
    #compete_cat
    #maj_agency_cat
    #psc_cat
    #setaside_cat
    #vendor_type
    #PoPCD
    #name_type
    #ParentCompany
    #vendor_cd
    #pop_cd
    #data_src
    #mod_agency
    #mod_eeduns
    #mod_dunsid
    #mod_fund_agency
    #maj_fund_agency_cat
    #mod_name
    #mod_parent
    #mod_sort
    #ProgSourceAgency
    #ProgSourceAccount
    #ProgSourceSubAcct
    #rec_flag
    
    ########### ?????
    #modnumber
    #IDVAgencyID
    #IDVPIID
    #IDVModificationNumber
    #fundedByForeignEntity
    #seaTransportation
    #letterContract
    #DavisBaconAct
    #ClingerCohenAct
    #serviceContractAct
    #WalshHealyAct
    #interagencyContractingAuthority, otherStatutoryAuthority_gen
    #useOfEPADesignatedProducts
    #vendorAlternateName
    #vendorLegalOrganizationName
    #vendorEnabled
    #smallBusinessFlag
    #smallBusinessFlag
    #firm8AFlag
    #HUBZoneFlag
    #SDBFlag
    #shelteredWorkshopFlag
    #HBCUFlag
    #educationalInstitutionFlag
    #womenOwnedFlag
    #veteranOwnedFlag
    #SRDVOBFlag
    #localGovernmentFlag
    #minorityInstitutionFlag
    #AIOBFlag
    #stateGovernmentFlag
    #federalGovernmentFlag
    #minorityOwnedBusinessFlag
    #APAOBFlag
    #tribalGovernmentFlag
    #BAOBFlag
    #NAOBFlag
    #SAAOBFlag
    #nonprofitOrganizationFlag
    #HAOBFlag
    #verySmallBusinessFlag
    #hospitalFlag
    #vendorSiteCode
    #vendorAlternateSiteCode
    #registrationDate
    #vendorLocationDisableFlag
    #contractingOfficerBusinessSizeDetermination
    #competitiveProcedures
    #solicitationProcedures
    #evaluatedPreference
    #research
    #statutoryExceptionToFairOpportunity
    #commercialItemAcquisitionProcedures
    #commercialItemTestProgram
    #smallBusinessCompetitivenessDemonstrationProgram
    #preAwardSynopsisRequirement
    #synopsisWaiverException
    #alternativeAdvertising
    #A76Action
    #localAreaSetAside
    #claimantProgramCode