# Search Methods

## Common Parameters

Unless otherwise specified, all search methods respond to
`page` and `per_page` parameters.

Additionally, most results are available in JSON, CSV, or XLS formats, 
via changing the extension of the request file.

## Bulk Data

The datasets behind each of these search methods&mdash;as well as several
additional datasets&mdash;are available in bulk. See the [Bulk Data page](bulk_data.html)
for more information.

## Methods

### Campaign Contributions

Search for itemized campaign contributions at the federal (FEC) or
state (NIMSP) level.

    /contributions.:format

#### Parameters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>`amount`</td>
            <td>`comparison`</td>
            <td>The amount of the contribution in US dollars.</td>
        </tr>
        <tr>
            <td>`contributor_ft`</td>
            <td>`string`</td>
            <td>Full-text search on the name of the contributing individual,
                PAC, organization or employer.
            </td>
        </tr>
        <tr>
            <td>`contributor_state`</td>
            <td>`inclusion`</td>
            <td>The two-letter state abbreviation from which the contribution
                was made, eg. DC.
            </td>
        </tr>
        <tr>
            <td>`cycle`</td>
            <td>`inclusion`</td>
            <td>The year (YYYY) of the election cycle.
            </td>
        </tr>
        <tr>
            <td>`date`</td>
            <td>`comparison`</td>
            <td>Date or date range of the contribution in ISO format.</td>
        </tr>
        <tr>
            <td>`for_against`</td>
            <td>`string`</td>
            <td>When organizations run ads against a candidate, they are counted
                as independent expenditures with the opposed candidate as the
                recipient. This parameter can be used to filter contributors meant
                for the candidate from those meant to be against the candidate.
            </td>
        </tr>
        <tr>
            <td>`organization_ft`</td>
            <td>`string`</td>
            <td>Full-text search on the name of the contributing employer,
                organization or parent organization.
            </td>
        </tr>
        <tr>
            <td>`recipient_ft`</td>
            <td>`string`</td>
            <td>Full-text search on the name of the PAC or candidate
                receiving the contribution.
            </td>
        </tr>
        <tr>
            <td>`recipient_state`</td>
            <td>`inclusion`</td>
            <td>The two-letter state abbreviation of the state in which the
                candidate receiving the contribution is running, eg. VA.
            </td>
        </tr>
        <tr>
            <td>`seat`</td>
            <td>`inclusion`</td>
            <td>The type of office being sought. Possible values include:
                <dl>
                    <dt>
                        `federal:senate`
                        <dd>US Senate</dd>
                    </dt>
                    <dt>
                        `federal:house`
                        <dd>US House of Representatives</dd>
                    </dt>
                    <dt>
                        `federal:president`
                        <dd>US President</dd>
                    </dt>
                    <dt>
                        `state:upper`
                        <dd>upper chamber of state legislature</dd>
                    </dt>
                    <dt>
                        `state:lower`
                        <dd>lower chamber of state legislature</dd>
                    </dt>
                    <dt>
                        `state:governor`
                        <dd>state governor</dd>
                    </dt>
                </dl>
            </td>
        </tr>
        <tr>
            <td>`seat_status`</td>
            <td>`string`</td>
            <td>`I` for incumbent, `O`for open. The
                value will be filled in where available in the source data.
            </td>
        </tr>
        <tr>
            <td>`seat_result`</td>
            <td>`string`</td>
            <td>`W` for win, `L` for loss. The value
                will be filled in where available in the source data.
            </td>
        </tr>
    </tbody>
</table>

#### Example

Get all DC contributions over $1000 in the 2012 election cycle:

    http://transparencydata.com/api/1.0/contributions.json?amount=%3E%7C1000&contributor_state=DC&cycle=2012&apikey=YOUR_KEY

#### Response

See the [schema documentation](contribution.html) for descriptions of the
response fields.

    [
        {
            "seat": "federal:president",
            "committee_ext_id": "C00431445",
            "seat_held": "federal:president",
            "recipient_party": "D",
            "transaction_type_description": "Transfer In Affiliated",
            "recipient_type": "P",
            "seat_status": "I",
            "recipient_state": "",
            "contributor_category": "Z4200",
            "contributor_gender": "",
            "contributor_state": "DC",
            "recipient_category": "Z1200",
            "is_amendment": true,
            "district": "",
            "organization_name": "Obama Victory Fund",
            "recipient_ext_id": "N00009638",
            "parent_organization_name": "",
            "contributor_address": "",
            "transaction_id": "pac2pac:2012:4013020121150134096",
            "contributor_occupation": "",
            "filing_id": "12950025570",
            "contributor_city": "WASHINGTON",
            "recipient_state_held": "",
            "district_held": "",
            "recipient_name": "Barack Obama (D)",
            "organization_ext_id": "C00494740",
            "contributor_zipcode": "20003",
            "transaction_namespace": "urn:fec:transaction",
            "date": "2011-06-30",
            "committee_name": "Obama for America",
            "candidacy_status": false,
            "parent_organization_ext_id": "",
            "cycle": 2012,
            "contributor_name": "Obama Victory Fund",
            "contributor_type": "C",
            "contributor_employer": "",
            "seat_result": "W",
            "transaction_type": "18g",
            "amount": "12750000.00",
            "contributor_ext_id": "C00494740",
            "committee_party": "D"
        },
        ...snip...
    ]

---

### Bundled Campaign Contributions

Search for itemized bundlers.

    /contributions/bundled.:format

#### Parameters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>`lobbyist_name`</td>
            <td>`string`</td>
            <td>The name of the lobbyist bundling on behalf of the recipient.</td>
        </tr>
        <tr>
            <td>`recipient_name`</td>
            <td>`string`</td>
            <td>The name of the politician or committee which received the bundled contribution.</td>
        </tr>
    </tbody>
</table>

#### Example

Get campaign contributions bundled by Patton Boggs.

    transparencydata.com/api/1.0/contributions/bundled.json?page=1&per_page=20&lobbyist_name=Patton%20Boggs&apikey=YOUR_KEY

#### Response

    [
        {
            "bundler_occupation": null,
            "bundler_name": "SU, PIPER NIETERS",
            "report_type": "QYS",
            "semi_annual_amount": 19000,
            "standardized_firm_name": "Patton Boggs LLP",
            "state": "DC",
            "street_addr2": null,
            "street_addr1": "2550 M STREET NW",
            "zip_code": "20037",
            "end_date": "2009-12-31",
            "city": "WASHINGTON",
            "committee_name": "BENNET FOR COLORADO",
            "committee_fec_id": "C00458398",
            "standardized_lobbyist_name": "Su, Piper",
            "report_year": 2009,
            "pdf_url": "http://query.nictusa.com/pdf/707/10020063707/10020063707.pdf",
            "standardized_recipient_name": "Michael F Bennet (D)",
            "start_date": "2009-10-01",
            "bundler_employer": "PATTON BOGSS",
            "bundler_fec_id": null,
            "file_num": -248701,
            "period_amount": 19000
        },
        {
            "bundler_occupation": null,
            "bundler_name": "JONAS, JOHN",
            "report_type": "Q2S",
            "semi_annual_amount": 32000,
            "standardized_firm_name": "Patton Boggs LLP",
            "state": "VA",
            "street_addr2": null,
            "street_addr1": "5840 COLFAX AVE",
            "zip_code": "22311",
            "end_date": "2010-06-30",
            "city": "ALEXANDRIA",
            "committee_name": "EARL POMEROY FOR CONGRESS",
            "committee_fec_id": "C00266619",
            "standardized_lobbyist_name": "Jonas, John",
            "report_year": 2010,
            "pdf_url": "http://query.nictusa.com/pdf/844/10930945844/10930945844.pdf",
            "standardized_recipient_name": "Earl Pomeroy (D)",
            "start_date": "2010-01-01",
            "bundler_employer": "PATTON BOGGS, LLP",
            "bundler_fec_id": null,
            "file_num": 479579,
            "period_amount": 32000
        },
        {
            "bundler_occupation": "LEGISLATIVE COUNCIL",
            "bundler_name": "COWAN, MARK D MR",
            "report_type": "Q2S",
            "semi_annual_amount": 114500,
            "standardized_firm_name": "Patton Boggs LLP",
            "state": "VA",
            "street_addr2": null,
            "street_addr1": "1123 LITTON LANE",
            "zip_code": "22101",
            "end_date": "2012-06-30",
            "city": "MCLEAN",
            "committee_name": "REPUBLICAN NATIONAL COMMITTEE",
            "committee_fec_id": "C00003418",
            "standardized_lobbyist_name": "Cowan, Mark D",
            "report_year": 2012,
            "pdf_url": "http://query.nictusa.com/pdf/333/12952442333/12952442333.pdf",
            "standardized_recipient_name": "Republican National Cmte",
            "start_date": "2012-04-01",
            "bundler_employer": "PATTON BOGGS LLP",
            "bundler_fec_id": null,
            "file_num": 797251,
            "period_amount": 0
        }
    ]

---

### Contractor Misconduct

Search for itemized misconduct incident reports
    
    /misconduct.:format

#### Parameters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>`contractor`</td>
            <td>`string`</td>
            <td>The name of the contractor to search for.</td>
        </tr>
        <tr>
            <td>`contracting_party`</td>
            <td>`string`</td>
            <td>The FIPS code for the contracting agency.</td>
        </tr>
        <tr>
            <td>`date_year`</td>
            <td>`inclusion`</td>
            <td>The year in which a date significant to the incident occurred.</td>
        </tr>
        <tr>
            <td>`enforcement_agency`</td>
            <td>`string`</td>
            <td>The name of the agency responsible for the enforcement action.</td>
        </tr>
        <tr>
            <td>`instance`</td>
            <td>`string`</td>
            <td>Full-text search on the description of the misconduct instance.</td>
        </tr>
        <tr>
            <td>`penalty_amount`</td>
            <td>`comparison`</td>
            <td>The amount of the penalty, in US dollars.</td>
        </tr>
    </tbody>
</table>

#### Example

Get misconduct instances for SAIC in 2012:

    transparencydata.com/api/1.0/misconduct.json?page=1&per_page=20&contractor=SAIC&date_year=2012&apikey=YOUR_KEY

#### Response

    [
        {
            "disposition": "Deferred Prosecution Agreement",
            "penalty_amount": 500392977,
            "date_year": 2012,
            "date_significance": "Date of Settlement Announcement",
            "enforcement_agency": "Justice",
            "contractor": "SAIC",
            "instance": "CityTime Contract Fraud Settlement",
            "synopsis": "In March 2012, SAIC agreed to pay $500.4 million under a deferred prosecution agreement to resolve claims of fraud occurring on the CityTime information technology contract with New York City. SAIC admitted it failed to investigate and notify the city of claims that project manager Gerard Denault steered work to subcontractor Technodyne LLC in exchange for kickbacks. SAIC agreed to the filing of one count of conspiracy to commit wire fraud and agreed to disgorge proceeds\nof the offense, including $370.4 million in restitution to the city and a $130 million penalty. The charge will be dropped after 3 years if SAIC pays the money and cooperates with federal investigators. See related SAIC instances \"U.S. v. Denault (CityTime Contract Fraud)\" and \"U.S. v. Bell (CityTime Contract Fraud).",
            "url": "http://www.contractormisconduct.org/index.cfm/1,73,222,html?CaseID=1648",
            "contracting_party": "State/Local",
            "date": "2012-03-14",
            "misconduct_type": "Government Contract Fraud",
            "court_type": "Criminal"
        }
    ]

---

### Earmarks

Search itemized earmark requests through FY 2010.

    /earmarks.:format

#### Parameters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>`amount`</td>
            <td>`comparison`</td>
            <td>The final amount of the earmark.</td>
        </tr>
        <tr>
            <td>`bill`</td>
            <td>`string`</td>
            <td>The bill, section or subsection of the earmark.</td>
        </tr>
        <tr>
            <td>`city`</td>
            <td>`string`</td>
            <td>The city where the money will be spent.</td>
        </tr>
        <tr>
            <td>`description`</td>
            <td>`string`</td>
            <td>Full-text search on the description of the earmark request.</td>
        </tr>
        <tr>
            <td>`member`</td>
            <td>`string`</td>
            <td>Full-text search on the member of Congress requesting the earmark.</td>
        </tr>
        <tr>
            <td>`member_party`</td>
            <td>`inclusion`</td>
            <td>The party of the member requesting the earmark, D, R or I.</td>
        </tr>
        <tr>
            <td>`member_state`</td>
            <td>`inclusion`</td>
            <td>The 2-letter state abbreviation of the requesting member.</td>
        </tr>
        <tr>
            <td>`recipient`</td>
            <td>`string`</td>
            <td>Full-text search on the intended recipient, when known.</td>
        </tr>
        <tr>
            <td>`year`</td>
            <td>`inclusion`</td>
            <td>The YYYY-formatted fiscal year for which the earmark was requested.</td>
        </tr>
    </tbody>
</table>

#### Example

Get the biggest earmark for Alaska in FY 2010:

    transparencydata.com/api/1.0/earmarks.json?page=1&per_page=20&member_state=AK&year=2010&apikey=YOUR_KEY

#### Response

See the [schema documentation](earmark.html) for descriptions of the
response fields.

    [
        {
            "description": "Aviation Task Force Complex, Ph 1, Incr 1",
            "recipients": "",
            "notes": "",
            "bill": "Military Construction",
            "undisclosed": "",
            "locations": "Fort Wainwright, AK",
            "fiscal_year": 2010,
            "omni_amount": "0.00",
            "house_amount": "95000000.00",
            "senate_amount": "125000000.00",
            "bill_subsection": "",
            "members": "Sen. Lisa Murkowski (R-AK)",
            "bill_section": "Army",
            "final_amount": "95000000.00",
            "presidential": "m",
            "budget_amount": "0.00"
        }
    ]

---

### EPA ECHO

Search itemized EPA enforcement actions.

    /epa.:format

#### Parameters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>`case_name`</td>
            <td>`string`</td>
            <td>The name of the enforcement case.</td>
        </tr>
        <tr>
            <td>`case_num`</td>
            <td>`inclusion`</td>
            <td>One or more specific case numbers.</td>
        </tr>
        <tr>
            <td>`defendants`</td>
            <td>`string`</td>
            <td>Full-text search for the name(s) of the defendant companies.</td>
        </tr>
        <tr>
            <td>`first_date`</td>
            <td>`string`</td>
            <td>Start of a date range of the most recent date of significance to the case in ISO format.</td>
        </tr>
        <tr>
            <td>`last_date`</td>
            <td>`string`</td>
            <td>End of a date range of the most recent date of significance to the case in ISO format.</td>
        </tr>
        <tr>
            <td>`location_adresses`</td>
            <td>`string`</td>
            <td>Full-text search on all addresses associated with the case.</td>
        </tr>
        <tr>
            <td>`penalty`</td>
            <td>`comparison`</td>
            <td>Total penalties, in US dollars.</td>
        </tr>
    </tbody>
</table>

#### Example

Get enforcement actions against Massey Energy since 2005

    transparencydata.com/api/1.0/epa.json?page=1&per_page=20&defendants=Massey%20Energy&first_date=%3E%7C2005-01-01&apikey=YOUR_KEY

#### Response

See the [schema documentation](epa_echo.html) for descriptions of the
response fields.

    [
        {
            "penalty_enfotpa": 13300000,
            "penalty_enfccaa": "7100000",
            "penalty_enfcslp": 0,
            "first_date": "2005-07-25",
            "num_defendants": 5,
            "case_name": "MASSEY ENERGY COMPANY, ET. AL.(NATIONAL CASE)(LEAD)",
            "penalty": "20400000",
            "last_date": "2008-04-09",
            "penalty_enfops": 0,
            "first_date_significance": "DOJ",
            "penalty_enfotsa": 0,
            "location_addresses": "2 JERRY FORK ROAD, DRENNEN, WV 26667; 4 NORTH 4TH ST, RICHMOND, VA 23219-0000; HUTCHINSON BRANCH ROAD, SUMMERSVILLE, WV 26651; ROUTE 3, SYLVESTER, WV 25193",
            "penalty_enfcraa": 0,
            "last_date_significance": "FOE",
            "defendants": "ALEX ENERGY, ELK RUN COAL COMPANY, MASSEY ENERGY COMPANY, PEERLESS EAGLE COAL COMPANY, POWER MOUNTAIN COAL COMPANY",
            "case_num": "03-2005-0380"
        },
        {
            "penalty_enfotpa": 6700000,
            "penalty_enfccaa": "3300000",
            "penalty_enfcslp": 0,
            "first_date": "2006-09-28",
            "num_defendants": 28,
            "case_name": "MASSEY ENERGY CO. & SUBSIDIARIES (NATIONAL CASE)",
            "penalty": "10000000",
            "last_date": "2011-03-22",
            "penalty_enfops": 0,
            "first_date_significance": "DOJ",
            "penalty_enfotsa": 0,
            "location_addresses": "115 NORTH BIG CREEK RD, SIDNEY, KY 41564; 185 MIDDLE FORK WOLF CRK RD, INEZ, KY 41224; 194/BRUSHY CREEK RD, MOREE, KY 41250; 3185 MIDDLE FORK CRK RD, INEZ, KY 41224; 3185 MIDDLE FORK WOLF CRK RD, INEZ, KY 41224; 3185 MIDDLE FRK WOLF CRK RD, INEZ, KY 41224; 5263 STATE HWY 194 E, KIMPER, KY 41539; BENT BR RD, HATFIELD, KY 41514; CASSADY BRAND RD / KY 908, PREECE, KY 41224; DAVELLA RD & KY RT 3, DAVELLA, KY 41214; EMILY CRK & LONG BR RD, PILGRAM, KY 41250; FRALEY BRANCH RD / KY 468, SIDNEY, KY 41564; HWY 468, SIDNEY, KY 41564; KY 1434 & ALDRIDGE BRANCH RD, MOREE, KY 41250; KY 1439 & WHITE CABIN BR RD, MOREE, KY 41250; KY 1439 & WOLF CREEK RD, PREECE, KY 41224; KY 1714, PILGRIM, KY 41250; KY 194 & CR 6272, PHYLLIS, KY 41554; KY 292 & CULLER HOLLOW RD, AFLEX, KY 41529; KY 292 & KY 468, LOVELY, KY 41231; KY 292 & STRINGTOWN BR RD, RANSOM, KY 41558; KY 319 / KY 1056, MCCARR, KY 41544; KY 3419, RANSOM, KY 41558; KY 468 & COUNTY RT 7125, NOLAN WV, KY 00000; KY 468 & ELKINS FORK, VARNEY, KY 41571; KY 468 & HALFWAY BR RD, RURAL, KY 41514; KY 468 & LICK BR RD, HATFIELD, KY 41514; KY 468 & LONG BR RD, HATFIELD, KY 41514; KY 468 & ROCKHOUSE FORK RD, SIDNEY, KY 41564; KY 468 & SWINGE CAMP BR, RURAL, KY 41514; KY 612 & KY 468, TURKEY CREEK, KY 41570; KY 908 JCT & LYNN BARK FORK RD, PREECE, KY 41224; KY 908 / WALNUT FORK RD, MOREE, KY 41224; KY HWY 119, SIDNEY, KY 41564; KY RT 1439 & WOLF CREEK RD, PILGRIM, KY 41250; LONG FORK RD, SOUTH WILLIAMSON, KY 41503; MCGEE BR RD, MOREE, KY 41250; NOSBEN BRANCH RD & KY RT 612, RURAL, KY 25687; PEGS BRANCH RD WITH US 119, BELFRY, KY 41514; PIGEONROOST FORK / KY 1714, LAURA, KY 41250; PIGEONROOST FORK & KY 1714, SIDNEY, KY 41564; RIGHT FORK RD & PANTHER FORK RD, DAVELLA, KY 41214; ROCKHOUSE FORK RD WITH KY 468, HATFIELD, KY 41514; ROCKHOUSE FORK RD W/ KY 468, HATFIELD, KY 41514; ROCKHOUSE FORK W/ KY 468, SIDNEY, KY 41564; SANDLICK BRANCH RD & KY 3, INEZ, KY 41224; ST RT 1439 & ASHLOG BRANCH RD, MCCLURE, KY 41250; ST RT 1714 INTER EMILY CREEK, UNKNOWN, KY 00000; ST RTS 319 & 1056, RANSOM, KY 41531; UNKNOWN, UNKNOWN, KY 00000; UPPER LICK BR & LONG FRK, TURKEY CREEK, KY 41570; US 119 & PEGS BR RD, BELFRY, KY 41514; US 119 & ROAD FORK RD, SIDNEY, KY 41564; US 119 W & KY 468, SIDNEY, KY 41654; VENTERS BRANCH RD, DAVELLA, KY 41214; WALKER BRANCH RD JCT KY RT 194, GULNARE, KY 41501; WOLF CREEK & MAYNARD FORK RD, THOMAS, KY 41626",
            "penalty_enfcraa": 0,
            "last_date_significance": "SNDDL",
            "defendants": "ALEX ENERGY, INC., ARACOMA COAL COMPANY, INC., A.T. MASSEY COAL COMPANY, BANDMILL COAL CORPORATION, BIG BEAR MINING COMPANY, CLEAR FORK COAL COMPANY, DELBARTON MINING COMPANY, DUCHESS COAL COMPANY, ELK RUN COAL COMPANY, INC., GREEN VALLEY COAL COMPANY, INDEPENDENCE COAL COMPANY, INC., JACKS BRANCH COAL COMPANY, LONG FORK COAL COMPANY, MAJESTIC MINING, INC., MARFORK COAL COMPANY, INC., MARTIN COUNTY COAL CORPORATION, MASSEY COAL SERVICES, INC., MASSEY ENERGY COMPANY, NEW RIDGE MINING COMPANY, OMAR MINING COMPANY, PEERLESS EAGLE COAL COMPANY, PERFORMANCE COAL COMPANY, POWER MOUNTAIN COAL COMPANY, RAWL SALES & PROCESSING CO., ROAD FORK DEVELOPMENT COMPANY, INC., SIDNEY COAL COMPANY, INC., STIRRAT COAL COMPANY, TRACE CREEK COAL COMPANY",
            "case_num": "04-2006-9037"
        }
    ]

---

### FACA Memberships

Search for itemized Federal Advisory Committee memberships.

    /faca.:format

#### Parameters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>`affiliation`</td>
            <td>`string`</td>
            <td>The name of the affiliated organization.</td>
        </tr>
        <tr>
            <td>`agency_name`</td>
            <td>`string`</td>
            <td>The name of the agency associated with the committee.</td>
        </tr>
        <tr>
            <td>`committee_name`</td>
            <td>`string`</td>
            <td>The name of the advisory committee.</td>
        </tr>
        <tr>
            <td>`member_name`</td>
            <td>`string`</td>
            <td>Full-text search on the name of the affiliated organization.</td>
        </tr>
        <tr>
            <td>`year`</td>
            <td>`inclusion`</td>
            <td>The YYYY-formatted year(s) the member sat on the committee.</td>
        </tr>
    </tbody>
</table>

#### Example

Get committees Francis Collins sat on in 2012:

    transparencydata.com/api/1.0/faca.json?page=1&per_page=20&member_name=Francis%20Collins&year=2012&apikey=YOUR_KEY

#### Response



    [
        {
            "committee_url": "http://www.nih.gov/about/director/acd.htm",
            "member_firstlast": "FRANCIS COLLINS",
            "agency_abbr": "HHS",
            "end_date": "2013-12-31",
            "pay_plan": "Hourly or Daily Compensation plus Travel and Per Diem",
            "represented_group": "",
            "appointment_term": "No Fixed Term",
            "member_designation": "Regular Government Employee (RGE)",
            "org_id": null,
            "appointment_type": "Agency",
            "affiliation": "DIRECTOR",
            "agency_name": "Department of Health and Human Services",
            "member_name": "FRANCIS S COLLINS",
            "pay_source": "Executive Branch",
            "committee_name": "Advisory Committee to the Director, National Institutes of Health",
            "chair": true,
            "org_name": null,
            "start_date": "2009-08-17"
        },
        {
            "committee_url": "http://acd.od.nih.gov/",
            "member_firstlast": "FRANCIS COLLINS",
            "agency_abbr": "HHS",
            "end_date": "2012-12-31",
            "pay_plan": "Hourly or Daily Compensation plus Travel and Per Diem",
            "represented_group": "",
            "appointment_term": "4 years",
            "member_designation": "Regular Government Employee (RGE)",
            "org_id": null,
            "appointment_type": "Agency",
            "affiliation": "DIRECTOR",
            "agency_name": "Department of Health and Human Services",
            "member_name": "FRANCIS S COLLINS",
            "pay_source": "Executive Branch",
            "committee_name": "Advisory Committee to the Director, National Institutes of Health",
            "chair": true,
            "org_name": null,
            "start_date": "2009-08-16"
        },
        {
            "committee_url": "http://www.nih.gov/about/director/acd.htm",
            "member_firstlast": "FRANCIS COLLINS",
            "agency_abbr": "HHS",
            "end_date": "2012-12-31",
            "pay_plan": "Hourly or Daily Compensation plus Travel and Per Diem",
            "represented_group": "",
            "appointment_term": "4 years",
            "member_designation": "Regular Government Employee (RGE)",
            "org_id": null,
            "appointment_type": "Agency",
            "affiliation": "DIRECTOR",
            "agency_name": "Department of Health and Human Services",
            "member_name": "FRANCIS S COLLINS",
            "pay_source": "Executive Branch",
            "committee_name": "Advisory Committee to the Director, National Institutes of Health",
            "chair": true,
            "org_name": null,
            "start_date": "2009-08-16"
        },
        ...snip...
    ]

---

### Federal Contracts

Search for itemized federal contract awards.

    /contracts.:format

#### Parameters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>`agency_id`</td>
            <td>`inclusion`</td>
            <td>The FIPS code for the agency, eg. 51013. 
                ([More on FIPS](http://www.nist.gov/itl/fips.cfm))
            </td>
        </tr>
        <tr>
            <td>`contracting_agency_id`</td>
            <td>`inclusion`</td>
            <td>The FIPS code for the contracting agency.</td>
        </tr>
        <tr>
            <td>`current_amount`</td>
            <td>`comparison`</td>
            <td>Current value of the contract in US dollars.</td>
        </tr>
        <tr>
            <td>`fiscal_year`</td>
            <td>`inclusion`</td>
            <td>A YYYY-formatted year in which the grant was awarded, 2006 up 
                to the most recent fiscal year.
            </td>
        </tr>
        <tr>
            <td>`maximum_amount`</td>
            <td>`comparison`</td>
            <td>Maximum possible value of the contract in US dollars.</td>
        </tr>
        <tr>
            <td>`obligated_amount`</td>
            <td>`comparison`</td>
            <td>The amount obligated or de-obligated by the transaction
                in US dollars.</td>
        </tr>
        <tr>
            <td>`place_district`</td>
            <td>`inclusion`</td>
            <td>The contressional district in which the contract action
                will be performed, eg. 7.</td>
        </tr>
        <tr>
            <td>`place_state`</td>
            <td>`inclusion`</td>
            <td>The FIPS code for the state in which the contract action
                be performed, eg. 50.</td>
        </tr>
        <tr>
            <td>`requesting_agency_id`</td>
            <td>`inclusion`</td>
            <td>The FIPS code for the requesting agency.</td>
        </tr>
        <tr>
            <td>`signed_date`</td>
            <td>`comparison`</td>
            <td>The date of contract signature in ISO format.</td>
        </tr>
        <tr>
            <td>`vendor_city`</td>
            <td>`string`</td>
            <td>Full-text search on the name of the primary city in which the
                contractor does business.
            </td>
        </tr>
        <tr>
            <td>`vendor_district`</td>
            <td>`inclusion`</td>
            <td>The primary congressional district in which the contractor
                does business.
            </td>
        </tr>
        <tr>
            <td>`vendor_duns`</td>
            <td>`inclusion`</td>
            <td>The Dun &amp; Bradstreet number assigned to the corporate
                parent of the contractor.
            </td>
        </tr>
        <tr>
            <td>`vendor_name`</td>
            <td>`string`</td>
            <td>Full-text search on the name of the contractor.</td>
        </tr>
        <tr>
            <td>`vendor_parent_duns`</td>
            <td>`inclusion`</td>
            <td>The Dun &amp; Bradstreet nuber assigned to the corporate
                parent of the contractor.</td>
        </tr>
        <tr>
            <td>`vendor_state`</td>
            <td>`inclusion`</td>
            <td>The primary state in which the contractor does business,
                eg. NY.
            </td>
        </tr>
        <tr>
            <td>`vendor_zipcode`</td>
            <td>`inclusion`</td>
            <td>The primary zipcode in which the contractor does
                business, eg. 20036.
            </td>
        </tr>
    </tbody>
</table>

#### Example

Get the largest contract awarded to L-3 Communications in FY 2012:

    http://transparencydata.com/api/1.0/contracts.json?per_page=1&fiscal_year=2012&vendor_duns=618019632&apikey=YOUR_KEY

#### Response

See the [schema documentation](contract.html) for descriptions of the
response fields.

    [
      {
        "contractingofficeid": "W911QY",
        "srdvobflag": false,
        "reasonnotcompeted": "",
        "seatransportation": "U",
        "hubzoneflag": false,
        "contractbundling": "D",
        "hbcuflag": false,
        "annualrevenue": "12000000000.00",
        "majorprogramcode": "",
        "firm8aflag": false,
        "smallbusinesscompetitivenessdemonstrationprogram": null,
        "tribalgovernmentflag": false,
        "apaobflag": false,
        "emergingsmallbusinessflag": false,
        "naobflag": false,
        "idvpiid": "W911QY10D0057",
        "locationcode": "",
        "isserviceprovider": null,
        "extentcompeted": "A",
        "hospitalflag": false,
        "effectivedate": "2012-03-23",
        "reasonformodification": "",
        "agency_name": "",
        "receivesgrants": "Y",
        "purchasecardaspaymentmethod": false,
        "numberofactions": 1,
        "phoneno": "8563383645",
        "idvmodificationnumber": "0",
        "localareasetaside": "N",
        "agencyid": "9700",
        "countryoforigin": "USA",
        "educationalinstitutionflag": false,
        "contractactiontype": "DO",
        "multiyearcontract": false,
        "saaobflag": false,
        "consolidatedcontract": false,
        "subcontractplan": "",
        "manufacturingorganizationtype": "A",
        "federalgovernmentflag": false,
        "rec_flag": null,
        "typeofsetaside": "NONE",
        "fundingrequestingofficeid": "W81XAG",
        "competitiveprocedures": "",
        "streetaddress": "1 FEDERAL ST",
        "costaccountingstandardsclause": "",
        "transaction_status": "active",
        "mod_agency": "2100",
        "nonprofitorganizationflag": false,
        "vendorenabled": "",
        "ultimatecompletiondate": "2013-05-31",
        "vendorlegalorganizationname": "L-3 COMMUNICATIONS CORPORATION",
        "gfe_gfp": true,
        "programacronym": "",
        "research": "",
        "state": "NJ",
        "statutoryexceptiontofairopportunity": "",
        "recoveredmaterialclauses": "C",
        "contingencyhumanitarianpeacekeepingoperation": "X",
        "haobflag": false,
        "descriptionofcontractrequirement": "DELIVERY ORDER 0003 OF THE BATTLEFIELD ANTI-INTRUSION SYSTEM (BAIS)",
        "receivescontracts": "Y",
        "vendorlocationdisableflag": null,
        "vendoralternatesitecode": "081031004",
        "maj_fund_agency_cat": "97",
        "placeofperformancezipcode": "081031004",
        "obligatedamount": "18099998.00",
        "davisbaconact": false,
        "parentdunsnumber": "008898843",
        "costorpricingdata": "N",
        "multipleorsingleawardidc": "",
        "minorityinstitutionflag": false,
        "contractfinancing": "F",
        "principalnaicscode": "334220",
        "fundingrequestingagencyid": "2100",
        "lastdatetoorder": "",
        "stategovernmentflag": false,
        "claimantprogramcode": "A7",
        "walshhealyact": true,
        "commercialitemtestprogram": false,
        "mod_parent": "L-3 COMMUNICATIONS HOLDINGS  INC.",
        "baseandalloptionsvalue": "18099998.00",
        "placeofmanufacture": "D",
        "fiscal_year": 2012,
        "vendoralternatename": "COMMUNICATION SYSTEMS - EAST DIVISION",
        "minorityownedbusinessflag": false,
        "priceevaluationpercentdifference": "",
        "city": "CAMDEN",
        "numberofoffersreceived": 3,
        "commercialitemacquisitionprocedures": "D",
        "veteranownedflag": false,
        "evaluatedpreference": "NONE",
        "informationtechnologycommercialitemcategory": "",
        "useofepadesignatedproducts": "A",
        "aiobflag": "N",
        "maj_agency_cat": "97",
        "psc_cat": "58",
        "transactionnumber": "0",
        "pop_cd": "NJ01",
        "baseandexercisedoptionsvalue": "18099998.00",
        "modnumber": "0",
        "idvagencyid": "9700",
        "organizationaltype": "CORPORATE NOT TAX EXEMPT",
        "statecode": "NJ",
        "solicitationprocedures": "NP",
        "congressionaldistrict": "NJ01",
        "vendorname": "L-3 COMMUNICATIONS CORPORATION",
        "productorservicecode": "5820",
        "receivescontractsandgrants": "Y",
        "currentcompletiondate": "2013-05-31",
        "performancebasedservicecontract": "X",
        "piid": "0003",
        "progsourcesubacct": "",
        "divisionname": "",
        "baobflag": false,
        "contracting_agency_name": "",
        "womenownedflag": false,
        "vendor_state_code": "NJ",
        "fedbizopps": "Y",
        "vendordoingasbusinessname": "",
        "ccrexception": "",
        "divisionnumberorofficecode": "",
        "unique_transaction_id": "f9454cb7766cc69b0a48e3655e58c87d",
        "localgovernmentflag": false,
        "servicecontractact": false,
        "systemequipmentcode": "000",
        "solicitationid": "W911QY10R0031",
        "sdbflag": false,
        "id": 1138460,
        "streetaddress3": "",
        "progsourceaccount": "2035",
        "zipcode": "081031004",
        "progsourceagency": "21",
        "interagencycontractingauthority": "X",
        "contractingofficeagencyid": "2100",
        "account_title": "",
        "vendorsitecode": "618019632",
        "numberofemployees": 64000,
        "streetaddress2": "",
        "vendorcountrycode": "UNITED STATES",
        "fundedbyforeignentity": "",
        "otherstatutoryauthority": "",
        "dunsnumber": "618019632",
        "placeofperformancecongressionaldistrict": "NJ01",
        "placeofperformancecountrycode": "US",
        "vendor_cd": "NJ01",
        "lettercontract": "X",
        "registrationdate": "2002-04-09",
        "shelteredworkshopflag": false,
        "contractingofficerbusinesssizedetermination": "O",
        "pop_state_code": "NJ",
        "typeofcontractpricing": "J",
        "faxno": "8563382741",
        "signeddate": "2012-03-23",
        "nationalinterestactioncode": "NONE",
        "a76action": false,
        "typeofidc": "",
        "renewaldate": "2011-03-08",
        "clingercohenact": false,
        "requesting_agency_name": ""
      }
    ]

---

### Federal Grants

Search for itemized federal grants.

    /grants.:format

#### Parameters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>`agency_ft`</td>
            <td>`string`</td>
            <td>Full-text search on the reported name of the federal
                agency awarding the grant.
            </td>
        </tr>
        <tr>
            <td>`amount_total`</td>
            <td>`comparison`</td>
            <td>Total amount of the grant in US dollars.</td>
        </tr>
        <tr>
            <td>`assistance_type`</td>
            <td>`inclusion`</td>
            <td>A general code for the type of grant awarded. Possible values include:
                <dl>
                    <dt>`10`</dt>
                    <dd>Direct payment with unrestricted use</dd>
                    <dt>`11`</dt>
                    <dd>Other reimbursable, contingent, intangible or
                        indirect financial assistance
                    </dd>
                    <dt>`02`</dt>
                    <dd>Block grant</dd>
                    <dt>`03`</dt>
                    <dd>Formula grant</dd>
                    <dt>`04`</dt>
                    <dd>Project grant</dd>
                    <dt>`05`</dt>
                    <dd>Cooperative agreement</dd>
                    <dt>`06`</dt>
                    <dd>Direct payment, as a subsidy or other non-reimbursable
                        direct financial aid
                    </dd>
                    <dt>`07`</dt>
                    <dd>Direct loan</dd>
                    <dt>`08`</dt>
                    <dd>Guaranteed/insured loan</dd>
                    <dt>`09`</dt>
                    <dd>Insurance</dd>
                </dl>
            </td>
        </tr>
        <tr>
            <td>`fiscal_year`</td>
            <td>`inclusion`</td>
            <td>The YYYY-formatted year in which the grant was awarded,
                from 2000 up to the most recent fiscal year.
            </td>
        </tr>
        <tr>
            <td>`recipient_ft`</td>
            <td>`string`</td>
            <td>Full-text search on the reported name of the grant recipient.</td>
        </tr>
        <tr>
            <td>`recipient_state`</td>
            <td>`inclusion`</td>
            <td>Two-letter postal abbreviation of the state in which the
                grant was awarded, eg. MD.</td>
        </tr>
        <tr>
            <td>`recipient_type`</td>
            <td>`inclusion`</td>
            <td>A general code for the type of entity that recieved the grant.
                possible values include:
                <dl>
                    <dt>`11`</dt>
                    <dd>Indian tribe</dd>
                    <dt>`12`</dt>
                    <dd>Other nonprofit</dd>
                    <dt>`20`</dt>
                    <dd>Private higher education</dd>
                    <dt>`21`</dt>
                    <dd>Individual</dd>
                    <dt>`22`</dt>
                    <dd>For-profit organization</dd>
                    <dt>`23`</dt>
                    <dd>Small business</dd>
                    <dt>`25`</dt>
                    <dd>Other</dd>
                    <dt>`00`</dt>
                    <dd>State government</dd>
                    <dt>`01`</dt>
                    <dd>County government</dd>
                    <dt>`02`</dt>
                    <dd>City or township government</dd>
                    <dt>`04`</dt>
                    <dd>Special district government</dd>
                    <dt>`05`</dt>
                    <dd>Independent school district</dd>
                    <dt>`06`</dt>
                    <dd>State-controlled institution of higher education</dd>
                </dl>
            </td>
        </tr>
    </tbody>
</table>

#### Example

Get the top grant given by USAID in FY 2012:

    http://transparencydata.com/api/1.0/grants.json?agency_ft=Agency%20For%20International%20Development&fiscal_year=2012&per_page=1&apikey=YOUR_KEY

#### Response

See the [schema documentation](grant.html) for descriptions of the
response fields.

    [
      {
        "progsrc_acnt_code": "1031",
        "principal_place_state": "00",
        "non_fed_funding_amount": "0.0",
        "rec_flag": null,
        "recipient_zip": "204330001",
        "fiscal_year": 2012,
        "progsrc_subacnt_code": "",
        "record_type": "2",
        "cfda_program_num": "98.001",
        "ending_date": "2013-09-30",
        "recipient_type": "25",
        "transaction_status": "active",
        "principal_place_cc": "FORGN",
        "face_loan_guran": "0",
        "principal_place_cd": "",
        "total_funding_amount": "1018158867",
        "orig_sub_guran": "0",
        "principal_place_code": "00FORGN",
        "agency_code": "7200",
        "recipient_county_code": "110",
        "assistance_type": "04",
        "uri": "AID-GHH-G-00-02-00002-17",
        "recipient_country_code": "USA",
        "maj_agency_cat": "72",
        "id": 6752773,
        "starting_date": "2002-06-04",
        "duns_conf_code": "0",
        "account_title": "Global Health and Child Survival",
        "project_description": "936-3110",
        "recipient_city_code": "50000",
        "duns_no": "062024112NONE",
        "recipient_county_name": "District of Columbia",
        "cfda_program_title": "USAID Foreign Assistance for Programs Overseas",
        "recip_cat_type": "o",
        "sai_number": "SAI NOT AVAILABLE",
        "obligation_action_date": "2012-06-22",
        "fyq": "",
        "progsrc_agen_code": "19",
        "federal_award_mod": "0017",
        "principal_place_state_code": "",
        "recipient_name": "WORLD BANK OFFICE OF THE PUBLISHER",
        "receip_addr2": "",
        "receip_addr3": "",
        "receip_addr1": "1818 H ST NW",
        "recipient_cd": "",
        "recipient_city_name": "WASHINGTON",
        "federal_award_id": "AIDGHHG000200002",
        "fed_funding_amount": "1018158867",
        "recipient_state_code": "DC",
        "unique_transaction_id": "be98113966b2de11d48108fc54a31f04",
        "agency_name": "AGENCY FOR INTERNATIONAL DEVELOPMENT",
        "principal_place_zip": "",
        "fyq_correction": "",
        "action_type": "B",
        "correction_late_ind": "",
        "asst_cat_type": "g"
      }
    ]

---

### Federal Lobbying

Search itemized federal lobbying reports.

    /lobbying.:format

#### Parameters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>`amount`</td>
            <td>`comparison`</td>
            <td>The amount spent on lobbying in US dollars.</td>
        </tr>
        <tr>
            <td>`client_ft`</td>
            <td>`string`</td>
            <td>Full-text search on the name of the client for which the
                lobbyist is working.
            </td>
        </tr>
        <tr>
            <td>`client_parent_ft`</td>
            <td>`string`</td>
            <td>Full-text search on the name of the parent organization
                of the client.
            </td>
        </tr>
        <tr>
            <td>`filing_type`</td>
            <td>`inclusion`</td>
            <td>The type of filing as identified by CRP. CRP recommends
                you observe the following rules:
                <ul>
                    <li>Do not total `e` records unless
                        they are larger than the associated
                        `s` record.
                    </li>
                    <li>Count `c` records in both total
                        and industry when `filing_included_nsfs`
                        is `n`. Don't count it in total or industry
                        when `filing_included_nsfs` is `y`.</li>
                    <li>Count `b` records in both total and
                        industry when `filing_included_nsfs`
                        is `n`. Exclude from total, and include
                        in industry&mdash;but subtract it from the total
                        of the parent&mdash;when `filing_included_nsfs`
                        is `y`.</li>
                </ul>
                Possible values include:
                <dl>
                    <dt>`n`</dt>
                    <dd>non self filer parent</dd>
                    <dt>`m`</dt>
                    <dd>non self filer subsidiary for a non self filer parent</dd>
                    <dt>`x`</dt>
                    <dd>self filer subsidiary for a non self filer parent</dd>
                    <dt>`p`</dt>
                    <dd>self filer parent</dd>
                    <dt>`i`</dt>
                    <dd>non self filer for a self filer parent that has
                        same catorder as the parent
                    </dd>
                    <dt>`s`</dt>
                    <dd>self filer subsidiary for a self filer parent</dd>
                    <dt>`e`</dt>
                    <dd>non self filer subsidiary for a self filer subsidiary</dd>
                    <dt>`c`</dt>
                    <dd>non self filer subsidiary for a self filer parent with
                        same catorder</dd>
                    <dt>`b`</dt>
                    <dd>non self filer subsidiary for a self filer parent that
                        has different catorder
                    </dd>
                </dl>
            </td>
        </tr>
        <tr>
            <td>`lobbyist_ft`</td>
            <td>`string`</td>
            <td>Full-text search on the name of the lobbyist involved in
                the lobbying activity.</td>
        </tr>
        <tr>
            <td>`registrant_ft`</td>
            <td>`string`</td>
            <td>Full-text search on the name of the person or organization
                filing the lobbyist registration. This is typically the
                firm that employs the lobbyists. Use the `registrant_is_firm`
                field in the response object to filter on firms vs. individuals.</td>
        </tr>
        <tr>
            <td>`transaction_id`</td>
            <td>`inclusion`</td>
            <td>Report ID given by the Senate Office of Public Records</td>
        </tr>
        <tr>
            <td>`transaction_type`</td>
            <td>`inclusion`</td>
            <td>The type of filing as reported by the Senate Office of
                Public Records. A current CSV of allowed values can be
                found here: [transaction_types-20130207.csv](http://assets.transparencydata.org.s3.amazonaws.com/docs/transaction_types-20130207.csv).
            </td>
        </tr>
        <tr>
            <td>`year`</td>
            <td>`inclusion`</td>
            <td>The year in which the registration was filed. A YYYY formatted
                year, 1998 to the most recent election year.
            </td>
        </tr>
    </tbody>
</table>

#### Example

Get the top registration, dollarwise, in 2012 by Patton Boggs:

    transparencydata.com/api/1.0/lobbying.json?per_page=1&registrant_ft=Patton%20Boggs&year=2012&apikey=YOUR_KEY


#### Response

See the [schema documentation](lobbying.html) for descriptions of the
response fields.

    [
      {
        "registrant_name": "Patton Boggs LLP",
        "filing_type": "n",
        "client_category": "E1100",
        "client_name": "Ivanishvili, Bidzina",
        "agencies": [
          {
            "agency_name": "Dept of State",
            "agency_ext_id": "039 "
          },
          {
            "agency_name": "Dept of Treasury",
            "agency_ext_id": "041 "
          },
          {
            "agency_name": "Export-Import Bank of the US",
            "agency_ext_id": "051 "
          },
          {
            "agency_name": "Federal Reserve System",
            "agency_ext_id": "062 "
          },
          {
            "agency_name": "US House of Representatives",
            "agency_ext_id": "002 "
          },
          {
            "agency_name": "US Senate",
            "agency_ext_id": "001 "
          },
          {
            "agency_name": "White House",
            "agency_ext_id": "012 "
          }
        ],
        "transaction_type": "q1a",
        "client_parent_name": "Ivanishvili, Bidzina",
        "amount": "510000.00",
        "transaction_id": "B7025EBA-41B8-4FB4-AECB-75BD5E8306F3",
        "lobbyists": [
          {
            "member_of_congress": false,
            "candidate_ext_id": null,
            "government_position": null,
            "lobbyist_name": "Harris, Laurence",
            "lobbyist_ext_id": "Y0000040336L"
          },
          {
            "member_of_congress": false,
            "candidate_ext_id": null,
            "government_position": null,
            "lobbyist_name": "Norman, W Caffrey",
            "lobbyist_ext_id": "Y0000003857L"
          },
          {
            "member_of_congress": false,
            "candidate_ext_id": null,
            "government_position": "Sen.E.Kennedy,Intern,99;SenateJuducCom,LawClrck,05",
            "lobbyist_name": "Oresman, Matthew Scott",
            "lobbyist_ext_id": "Y0000002649L"
          },
          {
            "member_of_congress": false,
            "candidate_ext_id": null,
            "government_position": null,
            "lobbyist_name": "Wisner, Graham",
            "lobbyist_ext_id": "Y0000034763L"
          }
        ],
        "year": 2012,
        "transaction_type_desc": "FIRST QUARTER AMENDMENT",
        "registrant_is_firm": true,
        "issues": [
          {
            "specific_issue": "Issues related to free and fair elections in Georgia",
            "general_issue": "Foreign Relations",
            "general_issue_code": "FOR"
          },
          {
            "specific_issue": "Issues related to international banking.",
            "general_issue": "Banking",
            "general_issue_code": "BAN"
          }
        ]
      }
    ]
