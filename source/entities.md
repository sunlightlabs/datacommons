# Entity Lookups

## Methods

### Search by Name

Search for politicians, individuals, organizations or industries with a
given name.

    /entities.json

#### Parameters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Required</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>search</code></td>
            <td>Required</td>
            <td>The name to search for. Spaces should be URL encoded or
                represented as a plus sign (+). There are no logical
                operators or grouping
            </td>
        </tr>
        <tr>
            <td><code>type</code></td>
            <td></td>
            <td>Filter results to a particular type of entity. Possible
                values are
                <code>politician</code>,
                <code>organization</code>,
                <code>individual</code> or
                <code>industry</code>.
            </td>
        </tr>
    </tbody>
</table>

#### Example

    http://transparencydata.org/api/1.0/entities.json?apikey=YOUR_KEY&search=Barack+Obama&type=politician

#### Response

    [
        {
            name: "Barack Obama (D)",
            count_given: 0,
            firm_income: 0,
            count_lobbied: 0,
            seat: "federal:president",
            total_received: 656313987,
            state: "",
            lobbying_firm: null,
            count_received: 1164442,
            party: "D",
            total_given: 0,
            type: "politician",
            id: "4148b26f6f1c437cb50ea9ca4699417a",
            non_firm_spending: 0,
            is_superpac: null
        },
        {
            name: "OBAMA, BARACK",
            count_given: 0,
            firm_income: 0,
            count_lobbied: 0,
            seat: "state:upper",
            total_received: 445595.36,
            state: "IL",
            lobbying_firm: null,
            count_received: 892,
            party: "D",
            total_given: 0,
            type: "politician",
            id: "97737bb56b6a4211bcc57a837368b1a4",
            non_firm_spending: 0,
            is_superpac: null
        }
    ]

This call can result in multiple response objects. In this case, we get
a hit for President Obama in the context of Illinois Senate races and
in presidential elections.

---

### ID Lookup

Crosswalk between several input ID forms and the transparencydata IDs
native to this service.

    /entities/id_lookup.json

#### Paramteters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Required</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>id</code></td>
            <td>Required, if supplied with <code>namespace</code></td>
            <td>The entity ID to look up
            </td>
        </tr>
        <tr>
            <td><code>namespace</code></td>
            <td>Required, if supplied with <code>id</code></td>
            <td>The type of ID to match. Possible values are:  
  
                <dl>
                    <dt><code>urn:crp:individual</code></dt>
                    <dd>A CRP ID for an individual contributor or 
                        lobbyist.  
                        Begins with <code>U</code> or
                        <code>C</code>.</dd>
                    <dt><code>urn:crp:organization</code></dt>
                    <dd>A CRP ID for an organization.  
                        Begins with
                        <code>D</code>.</dd>
                    <dt><code>urn:crp:recipient</code></dt>
                    <dd>A CRP ID for a politician.  
                        Begins with
                        <code>N</code>.</dd>
                    <dt><code>urn:crp:industry</code></dt>
                    <dd>CRP's 3-letter category order.</dd>
                    <dt><code>urn:crp:subindustry</code></dt>
                    <dd>CRP's 5-letter category code.</dd>
                    <dt><code>urn:nimsp:organization</code></dt>
                    <dd>A NIMSP ID for an organization.  
                        Integer-valued.</dd>
                    <dt><code>urn:nimsp:recipient</code></dt>
                    <dd>A NIMSP ID for a politician.  
                        Integer-valued.</dd>
                    <dt><code>urn:nimsp:subindustry</code></dt>
                    <dd>NIMSP's 5-letter category code.</dd>
                    <dt><code>urn:sunlight:
lobbyist_registration_tracker_url</code></dt>
                    <dd>URL of Sunlight's lobbyist registration tracker
                        page.</dd>
                </dl>
            </td>
        </tr>
        <tr>
            <td><code>bioguide_id</code></td>
            <td>Required, if <code>namespace</code> and <code>id</code>
                are omitted.</td>
            <td>The ID of a member of congress in the
                [Congressional Bioguide](http://bioguide.congress.gov/biosearch/biosearch.asp).
                Mutually exclusive to the id/namespace parameters.</td>
        </tr>
    </tbody>
</table>

#### Example

    http://transparencydata.org/api/1.0/entities/id_lookup.json?apikey=YOUR_KEY&bioguide_id=L000551

#### Response

    [
        {
            "id": "6d1ec9c94ae748c6b86cc250761c6b13"
        }
    ]

---

### Entity Overview

General information about the given entity.

    /entities/:entity_id.json

#### Parameters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Required</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>entity_id</code></td>
            <td>Required</td>
            <td>The transparencydata ID to look up.
            </td>
        </tr>
        <tr>
            <td><code>cycle</code></td>
            <td></td>
            <td>Limit contribution totals to the given election cycle(s).
            </td>
        </tr>
    </tbody>
</table>

#### Example

    transparencydata.com/api/1.0/entities/97737bb56b6a4211bcc57a837368b1a4.json?apikey=YOUR_KEY

#### Response

    {
        "name": "OBAMA, BARACK",
        "totals": {
            "2004": {
                "faca_committee_count": 0,
                "faca_member_count": 0,
                "regs_submitted_docket_count": 0,
                "earmark_count": 0,
                "regs_docket_count": 0,
                "recipient_amount": 29350.11,
                "fec_summary_count": 0,
                "independent_expenditure_amount": 0,
                "non_firm_spending": 0,
                "grant_count": 0,
                "contract_amount": 0,
                "earmark_amount": 0,
                "loan_count": 0,
                "contract_count": 0,
                "contributor_count": 0,
                "regs_document_count": 0,
                "recipient_count": 44,
                "firm_income": 0,
                "regs_submitted_document_count": 0,
                "loan_amount": 0,
                "epa_actions_count": 0,
                "contractor_misconduct_count": 0,
                "fec_total_raised": 0,
                "lobbying_count": 0,
                "contributor_amount": 0,
                "grant_amount": 0
            }
            ...snip...
        },
        "external_ids": [
            {
                "namespace": "urn:nimsp:recipient",
                "id": "17677"
            }
        ],
        "type": "politician",
        "id": "97737bb56b6a4211bcc57a837368b1a4",
        "metadata": {
            "2004": {
                "district": "IL-13",
                "state": "IL",
                "seat_result": "",
                "district_held": "",
                "seat": "state:upper",
                "seat_held": "",
                "state_held": "",
                "seat_status": "",
                "party": "D"
            },
            ...snip...
            "bio": "<p>Barack Hussein Obama II (i /bəˈrɑːk huːˈseɪn oʊˈbɑːmə/; born August 4, 1961) is the 44th and current President of the United States. He is the first African American to hold the office. Obama previously served as a United States Senator from Illinois, from January 2005 until he resigned after his election to the presidency in November 2008.</p><p>A native of Honolulu, Hawaii, Obama is a graduate of Columbia University and Harvard Law School, where he was the president of the Harvard Law Review. He was a community organizer in Chicago before earning his law degree. He worked as a civil rights attorney in Chicago and taught constitutional law at the University of Chicago Law School from 1992 to 2004.</p>",
            "seat_held": "",
            "source_name": "wikipedia_info",
            "district": "IL-13",
            "federal_politician_entities": [
                {
                    "name": "Barack Obama (D)",
                    "type": "politician",
                    "id": "4148b26f6f1c437cb50ea9ca4699417a"
                }
            ],
            "seat_result": "",
            "district_held": "",
            "seat": "state:upper",
            "state": "IL",
            "bio_url": "http://en.wikipedia.org/wiki/Barack_Obama",
            "state_held": "",
            "seat_status": "",
            "party": "D",
            "entity": "97737bb56b6a4211bcc57a837368b1a4",
            "photo_url": "http://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Official_portrait_of_Barack_Obama.jpg/245px-Official_portrait_of_Barack_Obama.jpg"
        }
    }

