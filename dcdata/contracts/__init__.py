FPDS_FIELDS = (
    'version','agencyID','PIID','modNumber','transactionNumber','IDVAgencyID','IDVPIID',
    'IDVModificationNumber','signedDate','effectiveDate','currentCompletionDate','ultimateCompletionDate',
    'obligatedAmount','baseAndExercisedOptionsValue','baseAndAllOptionsValue','contractingOfficeAgencyID',
    'contractingOfficeID','fundingRequestingAgencyID','fundingRequestingOfficeID','purchaseReason',
    'fundedByForeignEntity','feePaidForUseOfService','contractActionType','typeOfContractPricing',
    'nationalInterestActionCode','reasonForModification','majorProgramCode','costOrPricingData',
    'solicitationID','costAccountingStandardsClause','descriptionOfContractRequirement','GFE_GFP',
    'seaTransportation','consolidatedContract','letterContract','multiYearContract',
    'performanceBasedServiceContract','contingencyHumanitarianPeacekeepingOperation',
    'contractFinancing','purchaseCardAsPaymentMethod','numberOfActions','WalshHealyAct',
    'serviceContractAct','DavisBaconAct','ClingerCohenAct','interagencyContractingAuthority',
    'otherStatutoryAuthority_gen','productOrServiceCode','contractBundling','claimantProgramCode',
    'principalNAICSCode','recoveredMaterialClauses','manufacturingOrganizationType','systemEquipmentCode',
    'informationTechnologyCommercialItemCategory','useOfEPADesignatedProducts','countryOfOrigin',
    'placeOfManufacture','vendorName','vendorAlternateName','vendorLegalOrganizationName',
    'vendorDoingAsBusinessName','vendorEnabled','smallBusinessFlag','firm8AFlag','HUBZoneFlag',
    'SDBFlag','shelteredWorkshopFlag','HBCUFlag','educationalInstitutionFlag','womenOwnedFlag',
    'veteranOwnedFlag','SRDVOBFlag','localGovernmentFlag','minorityInstitutionFlag','AIOBFlag',
    'stateGovernmentFlag','federalGovernmentFlag','minorityOwnedBusinessFlag','APAOBFlag',
    'tribalGovernmentFlag','BAOBFlag','NAOBFlag','SAAOBFlag','nonprofitOrganizationFlag',
    'HAOBFlag','verySmallBusinessFlag','hospitalFlag','numberOfEmployees','annualRevenue',
    'organizationalType','streetAddress','streetAddress2','streetAddress3','city','state','ZIPCode',
    'vendorCountryCode','vendorSiteCode','vendorAlternateSiteCode','DUNSNumber','parentDUNSNumber',
    'phoneNo','faxNo','divisionName','divisionNumberOrOfficeCode','congressionalDistrict','registrationDate',
    'renewalDate','vendorLocationDisableFlag','contractorName','CCRException',
    'contractingOfficerBusinessSizeDetermination','locationCode','stateCode','placeOfPerformanceCountryCode',
    'placeOfPerformanceZIPCode','placeOfPerformanceCongressionalDistrict','extentCompeted',
    'competitiveProcedures','solicitationProcedures','typeOfSetAside','evaluatedPreference','research',
    'statutoryExceptionToFairOpportunity','reasonNotCompeted','numberOfOffersReceived',
    'commercialItemAcquisitionProcedures','commercialItemTestProgram',
    'smallBusinessCompetitivenessDemonstrationProgram','preAwardSynopsisRequirement','synopsisWaiverException',
    'alternativeAdvertising','A76Action','fedBizOpps','localAreaSetAside','priceEvaluationPercentDifference',
    'subcontractPlan','reasonNotAwardedToSmallDisadvantagedBusiness','reasonNotAwardedToSmallBusiness',
    'createdBy','createdDate','lastModifiedBy','lastModifiedDate','status','agencyspecificID',
    'offerorsProposalNumber','PRNumber','closeoutPR','procurementPlacementCode','solicitationIssueDate',
    'contractAdministrationDelegated','advisoryOrAssistanceServicesContract','supportServicesTypeContract',
    'newTechnologyOrPatentRightsClause','managementReportingRequirements','propertyFinancialReporting',
    'valueEngineeringClause','securityCode','administratorCode','contractingOfficerCode','negotiatorCode',
    'COTRName','alternateCOTRName','organizationCode','contractFundCode','isPhysicallyComplete',
    'physicalCompletionDate','installationUnique','fundedThroughDate','cancellationDate',
    'principalInvestigatorFirstName','principalInvestigatorMiddleInitial','principalInvestigatorLastName',
    'alternatePrincipalInvestigatorFirstName','alternatePrincipalInvestigatorMiddleInitial',
    'alternatePrincipalInvestigatorLastName','fieldOfScienceOrEngineering','finalInvoicePaidDate','accessionNumber',
    'destroyDate','accountingInstallationNumber','otherStatutoryAuthority','wildFireProgram','eeParentDuns',
    'ParentCompany','PoPCD','fiscal_year','name_type','mod_name','mod_parent','record_id','parent_id',
    'award_id','idv_id','mod_sort','compete_cat','maj_agency_cat','psc_cat','setaside_cat','vendor_type',
    'vendor_cd','pop_cd','data_src','mod_agency','mod_eeduns','mod_dunsid','mod_fund_agency',
    'maj_fund_agency_cat','ProgSourceAgency','ProgSourceAccount','ProgSourceSubAcct','rec_flag',
)

ACTION_TYPES = (
    ('A', 'GWAC'),
    ('B', 'IDC'),
    ('C', 'FSS'),
    ('D', 'BOA'),
    ('E', 'BPA'),
)

PRICING_TYPES = (
    ('A', 'Fixed price redetermination'),
    ('B', 'Fixed price level of effort'),
    ('J', 'Firm fixed price'),
    ('K', 'Fixed price with EPA'),
    ('L', 'Fixed price incentive'),
    ('M', 'Fixed price award fee'),
    ('R', 'Cost plus award fee'),
    ('S', 'Cost no fee'),
    ('T', 'Cost sharing'),
    ('U', 'Cost plus fixed fee'),
    ('V', 'Cost plus incentive fee'),
    ('Y', 'Time and materials'),
    ('Z', 'Labor hours'),
    ('1', 'Order dependent'),
    ('2', 'Combination'),
    ('3', 'Other'),
)

NIA_CODES = (
    ('NONE', 'None'),
    ('H05K', 'Hurricane Katrina 2005'),
    ('H05O', 'Hurricane Ophelia 2005'),
    ('H05R', 'Hurricane Rita 2005'),
    ('H05W', 'Hurricane Wilma 2005'),
    ('W081', 'California Wildfires 2008'),
    ('F081', 'Midwest Storms and Flooding 2008'),
    ('H08G', 'Hurricane Gustav 2008'),
    ('H08H', 'Hurricane Hanna 2008'),
    ('H08I', 'Hurricane Ike 2008'),
    ('H06C', 'Hurricane Chris 2006'),
    ('H06E', 'Hurricane Ernesto 2006'),
    ('I09P', 'Inauguration 2009'),
    ('T10S', 'American Samoa Earthquake, Tsunami, and Flooding 2010'),
    ('Q10H', 'Haiti Earthquake 2010'),
    ('Q10G', 'Gulf Oil Spill 2010'),
)

MOD_REASONS = (
    ('A', 'Additional work'),
    ('B', 'Supplemental agreement for work within scope'),
    ('C', 'Funding only action'),
    ('D', 'Change order'),
    ('E', 'Terminate for default'),
    ('F', 'Terminate for convenience'),
    ('G', 'Exercise an option'),
    ('H', 'Definitize letter contract'),
    ('J', 'Novation agreement'),
    ('K', 'Close out'),
    ('L', 'Definitize change order'),
    ('M', 'Other administrative action'),
    ('N', 'Legal contract cancellation'),
    ('P', 'Rerepsentation of non-novated merger/acquisition'),
    ('R', 'Rerepresentation'),
    ('S', 'Change PIID'),
    ('T', 'Transfer action'),
    ('V', 'Vendor DUNS change'),
    ('W', 'Vendor address change'),
    ('X', 'Terminate for cause'),
)

COST_OBTAINED = (
    ('N', 'No'),
    ('W', 'Waived'),
    ('Y', 'Yes'),
)

YNX = (
    ('Y', 'Yes'),
    ('N', 'No'),
    ('X', 'N/A'),
)

FINANCING = (
    ('A', 'FAR 52.232-16 progress payments'),
    ('C', 'Percentage of completion progress payments'),
    ('D', 'Unusual progress payments or advance payments'),
    ('E', 'Commercial financing'),
    ('F', 'Performance-based financing'),
    ('Z', 'Not applicable'),
)

BUNDLING = (
    ('A', 'Mission critical'),
    ('B', 'OMB circular A-76'),
    ('C', 'Other'),
    ('D', 'Not a bundled requirement'),
)

RM_CLAUSES = (
    ('A', 'FAR 52.223-4 included'),
    ('B', 'FAR 52.223-4 and FAR 52.223-9 included'),
    ('C', 'No clauses included'),
)

ORG_TYPES = (
    ('A', 'U.S. owned business'),
    ('B', 'Other U.S. entity'),
    ('C', 'Foreign-owned business incorporated in the U.S.'),
    ('D', 'Foreign-owned business not incorporated in the U.S.'),
    ('O', 'Other foreign entity'),
)

COMMERCIAL = (
    ('A', 'Commercially available'),
    ('B', 'Other commercial item'),
    ('C', 'Non-developmental item'),
    ('D', 'Non-commercial item'),
    ('E', 'Commercial service'),
    ('F', 'Non-commercial service'),
    ('Z', 'Not an IT product or service'),
)

PRODUCT_ORIGIN = (
    ('A', 'In U.S. by foreign concern'),
    ('B', 'Outside the U.S.'),
    ('C', 'Not a manufactured product'),
    ('D', 'Manufactured in the U.S.'),
    ('E', 'Manufactured outside the U.S.; used outside the U.S.'),
    ('F', 'Manufactured outside the U.S.; for resale'),
    ('G', 'Manufactured outside the U.S.; trade agreements'),
    ('H', 'Manufactured outside the U.S.; commercial IT'),
    ('I', 'Manufactured outside the U.S.; public interest'),
    ('J', 'Manufactured outside the U.S.; not available domestically'),
    ('K', 'Manufactured outside the U.S.; unreasonable cost'),
    ('L', 'Manufactured outside the U.S.; DOD qualifying country'),
)

CCR_EXCEPTIONS = (
    ('1', 'Government-wide commercial purchase card'),
    ('2', 'Classified contracts'),
    ('3', 'Contracting officers deployed in the course of military operations'),
    ('4', 'Contracting officers conducting emergency operations'),
    ('5', 'Contracts to support unusual or compelling needs'),
    ('6', 'Awards to foreign vendors for work performed outside the United States'),
    ('7', 'Micro-purchases that do not use the EFT'),
)

COMPETITIVENESS = (
    ('A', 'Full and open competition'),
    ('B', 'Not available for competition'),
    ('C', 'Not competed'),
    ('D', 'Full and open competition after exclusion of sources'),
    ('E', 'Follow on to competed action'),
    ('F', 'Competed under SAP'),
    ('G', 'Not competed under SAP'),
    ('CDO', 'Competitive delivery order'),
    ('NDO', 'Non-competitive delivery order'),
)

SET_ASIDES = (
    ('NONE', 'No set aside used'),
    ('SBA', 'Small business set aside (total)'),
    ('SBP', 'Small business set aside (partial)'),
    ('8A', '8(a) competed'),
    ('8AN', '8(a) sole source'),
    ('8AC', 'SDB set aside'),
    ('HMT', 'HBCU or MI set aside (total)'),
    ('HMP', 'HBCU or MI set aside (partial)'),
    ('VSB', 'Very small business set aside'),
    ('ESB', 'Emerging small business set aside'),
    ('HZC', 'HUBZone set aside'),
    ('HZS', 'HUBZone sole source'),
    ('HS2', 'Combination HUBZone and 8(a)'),
    ('HS3', '8(a) with HUBZone preference'),
    ('BI', 'Buy Indian'),
    ('RSB', 'Reserved for small business'),
    ('VSA', 'Veteran set aside'),
    ('VSS', 'Veteran sole source'),
    ('SDVOSBC', 'Servide disabled veteran owned small business set aside'),
    ('SDVOSBS', 'Servide disabled veteran owned small business sole source'),
)

NOCOMPETE_REASONS = (
    ('UNQ', 'Unique source'),
    ('FOC', 'Follow-on contract'),
    ('UR', 'Unsolicited research proposal'),
    ('PDR', 'Patent or data rights'),
    ('UT', 'Utilities'),
    ('STD', 'Standardization'),
    ('ONE', 'Only one source'),
    ('URG', 'Urgency'),
    ('MES', 'Mobilization, essential R&D'),
    ('IA', 'International agreement'),
    ('OTH', 'Authorized by statute'),
    ('RES', 'Authorized resale'),
    ('NS', 'National security'),
    ('PI', 'Public interest'),
    ('MPT', 'Less than or equal to the MPT'),
    ('SP2', 'SAP non-competition'),
    ('BND', 'Brand name description'),
)

SUBCONTRACT_PLANS = (
    ('A', 'No subcontracting possibilities'),
    ('B', 'Plan not required'),
    ('C', 'Plan required, incentive not included'),
    ('D', 'Plan required, incentive included'),
    ('E', 'Plan required'),
)