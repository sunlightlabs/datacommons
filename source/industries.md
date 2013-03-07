# Industry Aggregates

## Common Parameters

Unless otherwise specified, all aggregate methods respond to
`entity_id`, `limit`, and `cycle` parameters.

## Methods

### Top Industries

By contributions given, in dollars.

    /aggregates/industries/top_:limit.json

#### Parameters

- **`cycle` and `limit` only, this method returns multiple entities.**

#### Example

Get the top 2 industries in the 2012 cycle.

    http://transparencydata.com/api/1.0/aggregates/industries/top_2.json?cycle=2006&apikey=YOUR_KEY

#### Response

    [
        {
            "count": "2133557",
            "amount": "455606030.42",
            "id": "cdb3f500a3f74179bb4a5eb8b2932fa6",
            "should_show_entity": true,
            "name": "UNKNOWN"
        },
        {
            "count": "80122",
            "amount": "290070135.52",
            "id": "0af3f418f426497e8bbf916bfc074ebc",
            "should_show_entity": true,
            "name": "SECURITIES & INVESTMENT"
        }
    ]

---

### Top Organizations

Top organizations in an industry by dollars contributed.

    /aggregates/industry/:entity_id/orgs.json

#### Example

Get the top organization in the Food & Beverage industry:

    http://transparencydata.com/api/1.0/aggregates/industry/165d820dd48441e1befdc47f3fa3d236/orgs.json?cycle=2012&limit=1&apikey=YOUR_KEY

#### Response

    [
        {
            "employee_amount": "521598.00",
            "total_amount": "913298.00",
            "total_count": "771",
            "name": "McDonald's Corp",
            "direct_count": "290",
            "employee_count": "481",
            "id": "721c64757c11435393edc49bb33d4c96",
            "direct_amount": "391700.00"
        }
    ]
