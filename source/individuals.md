# Individual Aggregates

## Common Parameters

Unless otherwise specified, all aggregate methods respond to
`entity_id`, `limit`, and `cycle` parameters.

## Methods

### Top Individuals

By contributions given, in dollars.

    /aggregates/indivs/top_:limit.json

#### Parameters

- **`cycle` and `limit` only, this method returns multiple entities.**

#### Example

    http://transparencydata.com/api/1.0/aggregates/indivs/top_1.json?cycle=2006&apikey=YOUR_KEY

#### Response

    [
        {
            "count": "37",
            "amount": "29175900.00",
            "name": "Adelson, Miriam",
            "id": "71a6e4f389764529b0c239dc58206e71"
        }
    ]

---

### Top Recipient Organizations

Top organizations to which this individual has donated, by dollars given.

    /aggregates/indiv/:entity_id/recipient_orgs.json

#### Example

Get Sheldon Adelson's top org in 2012:

    http//transparencydata.com/api/1.0/aggregates/indiv/a03df5d9b20e467fa0ceaefa94c4491e/recipient_orgs.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "count": "2",
            "recipient_entity": null,
            "amount": "10000000.00",
            "recipient_name": "Restore Our Future"
        }
    ]

---

### Top Recipient Politicians

Politicians to whom the individual has given the most money.

    /aggregates/indiv/:entity_id/recipient_pols.json

#### Example

Get Sheldon Adelson's top 2 politicians for 2012:

    http://transparencydata.com/api/1.0/aggregates/indiv/a03df5d9b20e467fa0ceaefa94c4491e/recipient_pols.json?cycle=2012&limit=2&apikey=YOUR_KEY

#### Response

    [
        {
            "count": "1",
            "state": "WI",
            "recipient_name": "WALKER, SCOTT",
            "amount": "250000.00",
            "recipient_entity": "e7ea9c83ea3d42a2b8f546d8c9e9873e",
            "party": "R"
        },
        {
            "count": "2",
            "state": "NJ",
            "recipient_name": "Shmuley Boteach (R)",
            "amount": "5000.00",
            "recipient_entity": "708fa957322544e9a2aa8c1f25b8bb97",
            "party": "R"
        }
    ]

---

### Party Breakdown

Details on how much an individual gave to each party.

    /aggregates/indiv/:entity_id/recipients/party_breakdown.json

#### Example

Get Warren Buffet's party breakdown:

    transparencydata.com/api/1.0/aggregates/indiv/cc768536a9434b9da6fef5846a16ee88/recipients/party_breakdown.json?cycle=2012&apikey=YOUR_KEY

#### Response

    {
        "Republicans": [
            "1",
            "2500.00"
        ],
        "Democrats": [
            "12",
            "52500.00"
        ]
    }

Response values are arrays of [number of contributions, total amount].

---

### Lobbying Registrants

A list of the lobbying firms which employed an individual.

    /aggregates/indiv/:entity_id/registrants.json

#### Example

Get top lobbying registrant for Bob Dole in 2012:

    http://transparencydata.com/api/1.0/aggregates/indiv/4d052c80ef184ce5a5e41e6d34dc452f/registrants.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "registrant_name": "Alston & Bird",
            "count": 59,
            "registrant_entity": "58acd6c557764eeeb8ac4433eb32975a"
        }
    ]

---

### Lobbying Clients

Clients an individual (lobbyist) was contracted to work for.

    /aggregates/indiv/:entity_id/clients.json

#### Example

Get top 2 lobbying clients for Bob Dole in 2012:

    http://transparencydata.com/api/1.0/aggregates/indiv/4d052c80ef184ce5a5e41e6d34dc452f/clients.json?cycle=2012&limit=2&apikey=YOUR_KEY

#### Response

    [
        {
            "count": 6,
            "client_name": "Environmental Pasteurization",
            "client_entity": "10e927f6afac4f5ebe15b7962fe448e3"
        },
        {
            "count": 6,
            "client_name": "Celgene Corp",
            "client_entity": "e72dacce7cc44cebaeed240d2f986407"
        }
    ]

---

### Lobbying Issues

Issue areas a lobbyist worked on.

    /aggregates/indiv/:entity_id/issues.json

#### Example

Get top 2 issues for Bob Dole in 2012:

    http://transparencydata.com/api/1.0/aggregates/indiv/4d052c80ef184ce5a5e41e6d34dc452f/issues.json?cycle=2012&limit=2&apikey=YOUR_KEY

#### Response

    [
        {
            "count": 18,
            "issue": "Health Issues"
        },
        {
            "count": 12,
            "issue": "Environment & Superfund"
        }
    ]
