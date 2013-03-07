# Politician Aggregates

## Common Parameters

Unless otherwise specified, all aggregate methods respond to
`entity_id`, `limit`, and `cycle` parameters.

## Methods

### Top Politicians

By contributions received, in dollars.

    /aggregates/pols/top_:limit.json

#### Parameters

- **`cycle` and `limit` only, this method returns multiple entities.**

#### Example

    http://transparencydata.com/api/1.0/aggregates/pols/top_1.json?cycle=2006&apikey=YOUR_KEY

#### Response

    [
        {
            "count": "5322",
            "name": "WESTLY, STEVE",
            "state": "CA",
            "seat": "state:governor",
            "amount": "45272319.37",
            "party": "D",
            "id": "44d550f60eb14260928f9365415e5644"
        }
    ]

---

### Top Contributors

The top contributing organizations to a given candidate. Giving is
broken down into money given directly (by the organization's PAC), versus
money given by individuals employed by or associated with the organization.

    /aggregates/pol/:entity_id/contributors.json

#### Example

Get Barack Obama's top donor from 2012:

    http://transparencydata.com/api/1.0/aggregates/pol/4148b26f6f1c437cb50ea9ca4699417a/contributors.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "employee_amount": "1161884.00",
            "total_amount": "1161884.00",
            "total_count": "2235",
            "name": "University of California",
            "direct_count": "0",
            "employee_count": "2235",
            "id": "0e85264c0c0e4dfb9a4b38cfc181f030",
            "direct_amount": "0"
        }
    ]

---

### Top Industries

Top contributing industries, ranked by dollars given.

    /aggregates/pol/:entity_id/contributors/industries.json

#### Example

Get Barack Obama's top contributing industry from 2012:

    http://transparencydata.com/api/1.0/aggregates/pol/4148b26f6f1c437cb50ea9ca4699417a/contributors/industries.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "count": "88315",
            "amount": "43633891.00",
            "id": "b21467ae32924f84ada9076535401a91",
            "should_show_entity": false,
            "name": "RETIRED"
        }
    ]

---

### Unknown Industries

Contribution count and total for a politician from unknown industries.

    /aggregates/pol/:entity_id/contributors/industries_unknown.json

#### Parameters

- **Does not support `limit`, as only a single aggregate is returned.**

#### Example

Get unknown industry contributions for Barack Obama in 2012:

    http://transparencydata.com/api/1.0/aggregates/pol/4148b26f6f1c437cb50ea9ca4699417a/contributors/industries_unknown.json?cycle=2012&apikey=YOUR_KEY

#### Response

    {
        "count": "141945",
        "amount": "69115733.00"
    }

---

### Top Sectors

Contribution totals by sector to a given politician.

    /aggregates/pol/:entity_id/contributors/sectors.json

#### Example

Get top sector for Barack Obama in 2012:

    http://transparencydata.com/api/1.0/aggregates/pol/4148b26f6f1c437cb50ea9ca4699417a/contributors/sectors.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "sector": "W",
            "count": "147016",
            "amount": "72870168.00"
        }
    ]

Sectors are codified by letter:

<dl>
    <dt><code>A</code></dt>
    <dd>Agribusiness</dd>
    <dt><code>B</code></dt>
    <dd>Communications/Electronics</dd>
    <dt><code>C</code></dt>
    <dd>Construction</dd>
    <dt><code>D</code></dt>
    <dd>Defense</dd>
    <dt><code>E</code></dt>
    <dd>Energy/Natural Resources</dd>
    <dt><code>F</code></dt>
    <dd>Finance/Insurance/Real Estate</dd>
    <dt><code>H</code></dt>
    <dd>Health</dd>
    <dt><code>K</code></dt>
    <dd>Lawyers and Lobbyists</dd>
    <dt><code>M</code></dt>
    <dd>Transportation</dd>
    <dt><code>N</code></dt>
    <dd>Misc. Business</dd>
    <dt><code>Q</code></dt>
    <dd>Ideology/Single Issue</dd>
    <dt><code>P</code></dt>
    <dd>Labor</dd>
    <dt><code>W</code></dt>
    <dd>Other</dd>
    <dt><code>Y</code></dt>
    <dd>Unknown</dd>
    <dt><code>Z</code></dt>
    <dd>Administrative Use</dd>
</dl>

---

### Local Breakdown

A breakdown of how much of the money raised by a politician came from
inside or outside their home state.

    /aggretages/pol/:entity_id/contributors/local_breakdown.json

#### Parameters

- **Does not support `limit`, as only a single aggregate is returned.**

#### Example

Get local breakdown for Barack Obama's 2002 Senate race:

    http://transparencydata.com/api/1.0/aggregates/pol/97737bb56b6a4211bcc57a837368b1a4/contributors/local_breakdown.json?cycle=2002&apikey=YOUR_KEY

#### Response

    {
        "In-State": [
            "96",
            "69925.00"
        ],
        "Out-of-State": [
            "3",
            "400.00"
        ]
    }

Values are an array of ["number of contributions", "total amount"]

---

### Contributor Type Breakdown

A breakdown of how much of the money raised came from individuals versus
organzations (PACs).

#### Parameters

- **Does not support `limit`, as only a single aggregate is returned.**

#### Example

Get a type breakdown of Obama's contributors for the 2012 cycle:

    http://transparencydata.com/api/1.0/aggregates/pol/4148b26f6f1c437cb50ea9ca4699417a/contributors/type_breakdown.json?cycle=2012&apikey=YOUR_KEY

#### Response

    {
        "Individuals": [
            "458162",
            "255754102.00"
        ],
        "PACs": [
            "7",
            "9700.00"
        ]
    }

---

### FEC Summary

Latest figures from the FEC's summary report.

#### Parameters

- **Does not support `cycle`, as the data returned only applies to the current or
    latest cycle**
- **Does not support `limit`, as only a single aggregate is returned.**

#### Example

Get Obama's latest FEC summary:

    http://transparencydata.com/api/1.0/aggregates/pol/4148b26f6f1c437cb50ea9ca4699417a/fec_summary.json?apikey=YOUR_KEY

#### Response

    {
        "contributions_pac": "0.00",
        "office": "P",
        "total_receipts_rank": 1,
        "max_rank": 40,
        "contributions_candidate": "5000.00",
        "transfers_in": "176450000.00",
        "cash_on_hand_rank": 2,
        "total_raised": "724607132.15",
        "disbursements": "729647986.73",
        "total_disbursements_rank": 1,
        "date": "2012-11-26",
        "contributions_indiv": "541012836.42",
        "contributions_party": "8610.28",
        "cash_on_hand": "5397399.35"
    }

---

### FEC Independent Expenditures

Top independent expenditures for and against a politician.

    /aggregates/pol/:entity_id/fec_indexp.json

#### Parameters

- **Does not support `cycle` or `limit`; returns all results from the latest cycle.**

#### Example

Get independent expenditures for Obama in the latest election cycle:

    http://transparencydata.com/api/1.0/aggregates/pol/4148b26f6f1c437cb50ea9ca4699417a/fec_indexp.json?apikey=YOUR_KEY

#### Response

    [
        {
            committee_name: "RESTORE OUR FUTURE, INC.",
            amount: "88572359.38",
            support_oppose: "Oppose",
            committee_entity: "a0951518abe24d7a95cb99dac25caf90"
        },
        {
            committee_name: "American Crossroads",
            amount: "84622440.84",
            support_oppose: "Oppose",
            committee_entity: "1f7f4dc28a5b42f78ce438c1215768c6"
        },
        ...snip...
    ]
