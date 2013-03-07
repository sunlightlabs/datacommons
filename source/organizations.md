# Organization Aggregates

## Common Parameters

Unless otherwise specified, all aggregate methods respond to
`entity_id`, `limit`, and `cycle` parameters.

## Methods

### Top Organizations

By contributions given, in dollars.

    /aggregates/orgs/top_:limit.json

#### Parameters

- **`cycle` and `limit` only, this method returns multiple entities.**

#### Example

    http://transparencydata.com/api/1.0/aggregates/orgs/top_1.json?cycle=2006&apikey=YOUR_KEY

#### Response

    [
        {
            "count": "10282",
            "amount": "106113365.64",
            "name": "National Education Assn",
            "id": "1b8fea7e453d4e75841eac48ff9df550"
        }
    ]

---

### Top Recipients

Top recipients of money from this organization, by dollars received.

    /aggregates/org/:entity_id/recipients.json

#### Example

Get the top recipient from the National Education Assn. in the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/org/1b8fea7e453d4e75841eac48ff9df550/recipients.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "total_amount": "250000.00",
            "employee_amount": "0",
            "name": "GREGG, JOHN R",
            "total_count": "3",
            "state": "IN",
            "direct_count": "3",
            "party": "D",
            "employee_count": "0",
            "id": "e7ed6fb386c74515837469f6c6f971f0",
            "direct_amount": "250000.00"
        }
    ]

---

### PAC Recipients

Top PACs receiving money from a given organization.

    /aggregates/org/:entity_id/recipient_pacs.json

#### Example

Get the top recipient PAC from the National Education Assn. in the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/org/1b8fea7e453d4e75841eac48ff9df550/recipient_pacs.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "employee_amount": "0",
            "total_amount": "10751430.77",
            "total_count": "46",
            "name": "WE ARE OHIO",
            "direct_count": "46",
            "employee_count": "0",
            "id": null,
            "direct_amount": "10751430.77"
        }
    ]

---

### Party Breakdown

Portion of giving from an organization that went to each party.

    /aggregates/org/:entity_id/recipients/party_breakdown.json

#### Parameters

- **`entity_id` and `cycle` only, returns a single breakdown result.**

#### Example

Get the NEA's Party Breakdown for 2012:

    http://transparencydata.com/api/1.0/aggregates/org/1b8fea7e453d4e75841eac48ff9df550/recipients/party_breakdown.json?cycle=2012&apikey=YOUR_KEY

#### Response

    {
        "Republicans": [
            "642",
            "1045235.33"
        ],
        "Other": [
            "318",
            "14643671.05"
        ],
        "Democrats": [
            "4367",
            "10816686.44"
        ]
    }

---

### State/Federal (Level) Breakdown

Portion of giving from an organization that went state candidates versus
federal candidates.

    /aggregates/org/:entity_id/recipients/level_breakdown.json

#### Parameters

- **`entity_id` and `cycle` only, returns a single breakdown result.**

#### Example

Get the NEA's State/Federal Breakdown for 2012:

    http://transparencydata.com/api/1.0/aggregates/org/1b8fea7e453d4e75841eac48ff9df550/recipients/level_breakdown.json?cycle=2012&apikey=YOUR_KEY

#### Response

    {
        "Federal": [
            "973",
            "12668027.00"
        ],
        "State": [
            "4396",
            "24352801.82"
        ]
    }

---

### Lobbing Registrants

Lobbying firms hired by an organization.

    /aggregates/org/:entity_id/registrants.json

#### Example

Get the top lobbying firm hired by Procter & Gamble in the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/org/9070ecd132f44963a369479e91950283/registrants.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "registrant_name": "Mehlman Vogel Castagnetti Inc",
            "count": 12,
            "amount": "520000.00",
            "registrant_entity": "8595a50e311d4b2fbca37ca0b1367676"
        }
    ]

---

### Lobbying Issues

Issue areas an organization has hired lobbyists for.

    /aggregates/org/:entity_id/issues.json

#### Example

Get the top 2 issue areas for Procter & Gamble in the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/org/9070ecd132f44963a369479e91950283/issues.json?cycle=2012&limit=2&apikey=YOUR_KEY

#### Response

    [
        {
            "count": 24,
            "issue": "Health Issues"
        },
        {
            "count": 20,
            "issue": "Taxes"
        }
    ]

---

### Bills

Bills an organization has lobbied on.

    /aggregates/org/:entity_id/bills.json

#### Example

Get the top 2 bills for Procter & Gamble in the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/org/9070ecd132f44963a369479e91950283/bills.json?cycle=2012&limit=2&apikey=YOUR_KEY

    [
        {
            "bill_no": 2735,
            "count": 9,
            "title": "To amend the Internal Revenue Code of 1986 to make permanent the look-through treatment of payments between related controlled foreign corporations.",
            "bill_type": "h",
            "bill_name": "H.R.2735",
            "congress_no": 112,
            "cycle": 2012
        },
        {
            "bill_no": 639,
            "count": 8,
            "title": "Currency Reform for Fair Trade Act",
            "bill_type": "h",
            "bill_name": "H.R.639",
            "congress_no": 112,
            "cycle": 2012
        }
    ]

---

### Lobbyists

Lobbyists hired by an organization.

    /aggregates/org/:entity_id/lobbyists.json

#### Example

Get the top lobbyist for Procter & Gamble in the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/org/9070ecd132f44963a369479e91950283/lobbyists.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "count": 12,
            "lobbyist_name": "BINGEL, KELLY",
            "lobbyist_entity": "8a0fa1c2d331499ba992d17b53336a49"
        }
    ]

---

### Registrant Clients

Top clients that hired an organization (lobbying firm).

    /aggregates/org/:entity_id/registrant/clients.json

#### Example

Get the top 2 clients for Patton Boggs in the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/org/52a1620b2ff543ebb74718fbff742529/registrant/clients.json?cycle=2012&limit=2&apikey=YOUR_KEY

#### Response

    [
        {
            "count": 6,
            "client_name": "Depository Trust & Clearing Corp",
            "client_entity": "bb5ac6cef3414fc3baba9cedf62d426a",
            "amount": "1680000.00"
        },
        {
            "count": 6,
            "client_name": "Wholesale Markets Brokers Assn Americas",
            "client_entity": "96eb8866f1574daea5fdef509348d87d",
            "amount": "1450000.00"
        }
    ]

---

### Registrant Issues

Top issue areas an organization (lobbying firm) has lobbied on.

    /aggregates/org/:entity_id/registrant/issues.json

#### Example

Get the top 2 issue areas for Patton Boggs in the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/org/52a1620b2ff543ebb74718fbff742529/registrant/issues.json?cycle=2012&limit=2&apikey=YOUR_KEY

#### Response

    [
        {
            "count": 369,
            "issue": "Fed Budget & Appropriations"
        },
        {
            "count": 241,
            "issue": "Transportation"
        }
    ]

---

### Registrant Bills

Top bills an organization (lobbying firm) has lobbied on.

    /aggregates/org/:entity_id/registrant/bills.json

#### Example

Get the top 2 bills for Patton Boggs in the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/org/52a1620b2ff543ebb74718fbff742529/registrant/bills.json?cycle=2012&limit=2&apikey=YOUR_KEY

#### Response

    [
        {
            "bill_no": 658,
            "count": 109,
            "title": "FAA Reauthorization and Reform Act of 2011",
            "bill_type": "h",
            "bill_name": "H.R.658",
            "congress_no": 112,
            "cycle": 2012
        },
        {
            "bill_no": 223,
            "count": 106,
            "title": "FAA Air Transportation Modernization and Safety Improvement Act",
            "bill_type": "s",
            "bill_name": "S.223",
            "congress_no": 112,
            "cycle": 2012
        }
    ]

---

### Registrant Lobbyists

Top lobbyists an organization (lobbying firm) employs, by registrations.

    /aggregates/org/:entity_id/registrant/lobbyists.json

#### Example

Get the top lobbyist for Patton Boggs in the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/org/52a1620b2ff543ebb74718fbff742529/registrant/lobbyists.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "count": 196,
            "lobbyist_name": "BREAUX, JOHN",
            "lobbyist_entity": "5d18bbc40f7e49938f21d0e2068741fc"
        }
    ]

---

### Mentions in Regulations

Regulatory dockets that most frequently mention an organization

    /aggregates/org/:entity_id/regulations_text.json

#### Example

Get the regulatory docket that mentions McDonald's the most in the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/org/721c64757c11435393edc49bb33d4c96/regulations_text.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "count": 11,
            "year": 2011,
            "agency": "DOS",
            "docket": "DOS-2011-0055",
            "title": "60–Day Notice of Proposed Information Collection: DS–5513, Biographical Questionnaire for U.S. \r\nPassport, 1405–XXXX"
        }
    ]

---

### Regulatory Comment Submissions

Regulatory dockets with the most comment submissions from an organization.

#### Example

Get the top docket for Procter & Gamble in the 2012 cycle:

    transparencydata.com/api/1.0/aggregates/org/9070ecd132f44963a369479e91950283/regulations_submitter.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "count": 2,
            "year": 2011,
            "agency": "FAA",
            "docket": "FAA-2011-0183",
            "title": "Notice of Proposed Modification to the June 1, 2006 MOA FAA/Subscriber Memorandum of Agreement for ASDI/NASSI Industry Access and Request for Comments"
        }
    ]

---

### FACA Memberships

Lists employees of an organization ith memberships on federal advisory committees.

    /aggregates/org/:entity_id/faca.json

#### Example

Get FACA memberships for Patton Boggs in the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/org/52a1620b2ff543ebb74718fbff742529/faca.json?cycle=2012&limit=10&apikey=YOUR_KEY


#### Response

    [
        {
            "committee_count": 1,
            "agency_abbr": "DOC",
            "agency_name": "Department of Commerce",
            "member_count": 1
        }
    ]

---

### FEC Summary

Latest figures for an organization from the FEC's summary report, current election cycle only.

    /aggregates/org/:entity_id/fec_summary.json

#### Parameters

- **Only supports `entity_id`, returns a single summary report from the latest figures**

#### Example

Get latest figures for Patton Boggs:

    http://transparencydata.com/api/1.0/aggregates/org/52a1620b2ff543ebb74718fbff742529/fec_summary.json?apikey=YOUR_KEY

#### Response

    {
        "independent_expenditures_made": "0.00",
        "loans_received": "0.00",
        "contributions_from_indiv": "439353.09",
        "nonfederal_transfers_received": "0.00",
        "transfers_from_affiliates": "0.00",
        "cash_on_hand": "110209.79",
        "num_committee_filings": 1,
        "total_raised": "449353.09",
        "debts": "0.00",
        "disbursements": "486694.29",
        "first_filing_date": "2012-11-26",
        "nonfederal_expenditure_share": "0.00",
        "last_filing_date": "2012-11-26",
        "contributions_to_committees": "474000.00",
        "party_coordinated_expenditures_made": "0.00",
        "contributions_from_pacs": "10000.00"
    }
