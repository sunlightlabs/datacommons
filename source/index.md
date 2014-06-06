Programmatic access tracking the influence of money in politics, brought
to you by  
the [Sunlight Foundation](http://sunlightfoundation.com).

## Features

### Entity Lookup and Crosswalk

Look up IDs for political entities by name, retrieve basic biographical
and other meta information, or find an entity ID from a variety of
source IDs, including:

- Bioguide
- CRP
- NIMSP
- Sunlight's Lobbyist Registration Tracker URL

### Itemized Data

Search and filter individual contributions, contracts, grants and
lobbying registrations.

### Aggregate Data

Find the most active Politicians, Individuals, Organizations and
Industries based on receipts, expenditures and lobbying.

### Support/Community
We have an
[API mailing list](https://groups.google.com/forum/?fromgroups#!forum/sunlightlabs-api-discuss),
and can be found on Twitter at
[@sunlightlabs](http://twitter.com/sunlightlabs).

## License

Data returned by this service is subject to the use restrictions set by
the [Federal Election Commission](http://www.fec.gov). By accessing this
data, you understand that you are using the data subject to all
applicable local, state and federal law, including FEC restrictions.

All data licensed under a
[Creative Commons BY-NC-SA license](http://creativecommons.org/licenses/by-nc-sa/3.0/us/).
By downloading data and accessing the API you are agreeing to the terms
of the license.

Federal campaign contribution and lobbying records must be attributed to
[OpenSecrets.org](http://www.opensecrets.org).

State campaign contribution records must be attributed to
[FollowTheMoney.org](www.followthemoney.org).

## Endpoints

All calls to the Influence Explorer API share the same root URI:

```text
http://transparencydata.com/api/:version/
```

The current verison is `1.0`.

The URI scheme is not strictly RESTful, but methods can be grouped into
6 logical categories:

<table>
    <thead>
        <tr>
            <th width="35%">Endpoint</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>**[Entity Lookups](entities.html)**</td>
            <td>Search for politicians, individuals, organizations and
                industries, or retrieve crosswalk IDs from a variety of
                sources.
            </td>
        </tr>
        <tr>
            <td>**[Politician Aggregates](politicians.html)**</td>
            <td>Find aggregate campaign finance information about political
                candidates at the state and federal levels.
            </td>
        </tr>
        <tr>
            <td>**[Individual Aggregates](individuals.html)**</td>
            <td>Find aggregate campaign finance information about individual
                donors.
            </td>
        </tr>
        <tr>
            <td>**[Organization Aggregates](organizations.html)**</td>
            <td>Find aggregate campaign finance information about organizations,
                including PACs, corporations and lobbying firms.
            </td>
        </tr>
        <tr>
            <td>**[Industry Aggregates](industries.html)**</td>
            <td>Find aggregate campaign finance information about various
                industries are involved in lobbying.
            </td>
        </tr>
        <tr>
            <td>**[Itemized Search Methods](search.html)**</td>
            <td>Search itemized campaign contributions, federal contract awards,
                federal grant awards and federal lobbying registrations.
            </td>
        </tr>
    </tbody>
</table>

## Common Parameters

### API Key

All requests to the Influence Explorer API require a Sunlight API key.
An API key is
[free to register](http://services.sunlightlabs.com/accounts/register/)
and has no usage limits.

API keys can be provided with a request through the query string:

    /entities.json?apikey=[your_api_key]

### Pagination / Limiting

All itemized endpoints respond to `page` and `per_page` parameters to
scroll through the data, passed like so:

    /contributions.json?page=2&per_page=100

By default, the first page is returned, with 1,000 records per page.
The maximum `per_page` value is 100,000.

### Aggregate Limiting / Cycle

Except where specified, all aggregate endpoints respond to `limit` and
`cycle` parameters, to limit the number of top results returned, and to
base superlative calculations on a given election year:

    /aggregates/pols/top_10.json?cycle=2012

In this example, the limit parameter is part of the method name (top_:limit).

### Ranges and OR Searches

Some parameters are specified in this documentation as the types
`comparison` or `inclusion`. These fields support logical operators
prepended to their values to denote a range of values or multiple
values to include:

#### Comparison (range)

<table>
    <tr>
        <td><code>&gt;|</code></td>
        <td>Greater than or equal to, eg. <code>&gt;|1000</code></td>
    </tr>
    <tr>
        <td><code>&lt;</code></td>
        <td>Less than, eg. <code>&lt;1000000</code></td>
    </tr>
    <tr>
        <td><code>&gt;&lt;||</code></td>
        <td>Between, eg. <code>&gt;&lt;|1000|5000</code></td>
    </tr>
</table>

#### Inclusion (boolean OR)

<dl>
    <dt>`2006|2008|2010`</dt>
    <dd>Include results from 2006, 2008 and 2010.</dd>
</dl>

## Client Libraries

- [PHP](http://github.com/dqminh/transparencydata-php) by Dao Quang Minh
- [Python](http://github.com/sunlightlabs/python-transparencydata) by
    The Sunlight Foundation
- [Ruby](http://github.com/pengwynn/transparency-data) by Wynn
    Netherland and Luigi Montanez

## Bulk Data

For analysis that requires access to large portions of our data, we
offer (and strongly encourage!) a bulk data set for free. See the
[Bulk Data page](bulk_data.html) for a list of available downloads.

## Data Changelog

#### June 2, 2014 Update

-   Federal Campaign Finance Data: updated to CRP's 5/5/2014 release.
-   Federal Lobbying Data: updated to CRP's 5/5/2014 release.

#### March 24, 2014 Update

-   Federal Campaign Finance Data: updated to CRP's 3/3/2014 release.

#### November 22, 2013 Update

-   Federal Campaign Finance Data: updated to CRP's 11/6/2013 release.
-   State Campaign Finance Data: updated to NIMSP's private 11/18/2013
    release.

#### October 30, 2013 Update

-   Federal Lobbying Data: updated to CRP's 10/10/2013 release.

#### July 26, 2013 Update

-   Federal and State Campaign Finance Data: Addressed data quality
    issues in all previous uploads. New versions of each previous
    release now available

#### July 25, 2013 Update

-   Federal Campaign Finance Data: updated to CRP's 6/1/2013 release.
-   State Campaign Finance Data: updated to NIMSP's private 7/3/2013
    release.

#### June 4, 2013 Update

-   Federal Lobbying Data: updated to CRP's 4/29/2013 release.

#### April 3, 2013 Update

-   Federal Campaign Finance Data: updated to CRP's 2/28/2013 release.
-   State Campaign Finance Data: updated to NIMSP's private 3/11/2013
    release.
-   Federal Lobbying Data: updated to CRP's 1/25/2013 release.

#### March 11, 2013 Update

-   Contractor Misconduct Data: updated to POGO's 3/5/2013 release.
-   Regulations Data: Influence Explorer now uses data from [Docket
    Wrench](http://docketwrench.sunlightfoundation.com), which is
    updated on a daily basis.

#### January 9, 2013

- Federal Campaign Finance Data: updated to CRP's 11/29/2012 release.

#### October 31, 2012

- State Campaign Finance Data: updated to private 10/18/2012 release.

#### October 25, 2012

- Federal Grants: updated to USASpending.gov's 10/19/2012 release.

#### October 15, 2012

- Federal Lobbying Data: updated to CRP's 9/21/2012 release.

#### August 31, 2012

- Federal Campaign Finance Data: updated to CRP's 8/24/2012 release.

#### April 23, 2012

- Federal Campaign Finance Data: updated to private 4/2/2012 CRP release.
- Contractor Misconduct Data: updated to POGO's 3/3/2012 release.

#### March 21, 2012

- Federal Campaign Finance Data: updated to private 3/16/2012 CRP release.
- State Campaign Finance Data: updated to private 3/13/2012 release.
- Federal Grants & Contracts: updated to USASpending.gov's 3/1/2012 release.
- Federal Advisory Committee Act: updated with GSA's release of 2011 data.

#### February 24, 2012

- Federal Campaign Finance Data: updated to private 2/15/2012 CRP release.
- State Campaign Finance Data: updated to NIMSP's 1/31/2012 release.

#### January 6, 2012

- Federal Lobbying Data: updated to CRP's 12/8/2011 release.
- Contractor Misconduct Data: updated to POGO's 12/21/2011 release.

#### October 27, 2011

-Federal Campaign Finance Data: updated to CRP's 10/3/2011 release.
-EPA ECHO Data: updated to 10/19/2011 release.

#### July 23, 2011

- Federal Campaign Finance Data: updated to CRP's 5/20/2011 release.
- State Campaign Finance Data: updated to NIMSP's 7/11/2011 release (private).

#### June 21, 2011

- Federal Lobbying Data: updated to CRP's 5/24/2011 release.
- Federal Grants & Contracts: updated to USASpending.gov's 6/1/2011 release.

#### June 6, 2011

- Contractor Misconduct Data: initial release of Project on Government Oversight's Federal Contractor Misconduct data, 1995-2011.

#### April 20, 2011

- Federal Campaign Finance Data: updated to CRP's 4/13/2011 release (private).
- Federal Lobbying Data: updated to CRP's 3/25/2011 release.
- State Campaign Finance Data: updated to NIMSP's March 2011 release (private).
- Federal Grants & Contracts: updated to USASpending.gov's 3/1/2011 release.

#### March 22, 2011

- Federal Lobbying Data: updated to CRP's 2/22/2011 release.
- Federal Grants & Contracts: updated to USASpending.gov's 3/1/2011 release.

#### February 1, 2011

- Federal Campaign Finance Data: updated to CRP's 1/8/2011 release.
- Federal Lobbying Data: updated to CRP's 11/15/2010 release.
- State Campaign Finance Data: updated to NIMSP's December 2010 release (private).
- Federal Grants & Contracts: updated to USASpending.gov's 1/1/2011 release.

#### December 2, 2010

- Earmark Data: initial release of Taxpayers for Common Sense's fiscal year 2008-2010 earmark data.

#### November 8, 2010

- Federal Campaign Finance Data: updated to CRP's 10/23/2010 release.
- Federal Lobbying Data: updated to CRP's 10/24/2010 release.

#### October 26, 2010

- Federal Campaign Finance Data: updated to CRP's 9/30/2010 release.
- State Campaign Finance Data: updated to NIMSP's September 2010 release (private).
- Federal Lobbying Data: updated to CRP's 9/20/2010 release.

#### September 9, 2010

- Federal Campaign Finance Data: updated to CRP's 8/23/2010 release.
- State Campaign Finance Data: updated to NIMSP's June 2010 release (private).
- Federal Lobbying Data: updated to CRP's 8/27/2010 release.
- Federal Grants & Contracts: provided by USASpending.gov on request in April 2010.

#### Initial Data

- All data current as of March 2010.
