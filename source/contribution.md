## Campaign Contributions Data Schema

<style>
    dd{ clear: left; margin-bottom: 1em; }
</style>
<dl>
    <dt>
        cycle
    </dt>
    <dd>
        The election cycle in which the transaction occurred. Valid values are
        even years between 1990 and 2010 (inclusive).
    </dd>
    <dt>
        transaction_namespace
    </dt>
    <dd>
        <p>Indicates the source of the transaction.</p>
        <table>
            <thead>
                <tr>
                    <th>Value</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>`urn:fec:transaction`</td>
                    <td>federal transactions (CRP)</td>
                </tr>
                <tr>
                    <td>`urn:nimsp:transaction`</td>
                    <td>state transactions (NIMSP)</td>
                </tr>
            </tbody>
        </table>
    </dd>
    <dt>
        transaction_id
    </dt>
    <dd>
        Unique record ID given to the transaction by the FEC (federal) or NIMSP
        (state). Federal records are only guaranteed to be unique per year so they
        are prepended with the cycle.
    </dd>
    <dt>
        transaction_type
    </dt>
    <dd>
        Federal records have transaction types assigned by the FEC. The transaction
        type indicates whether the record is, for instance, a contribution, an
        independent expenditure, a loan or one of many more esoteric types. The
        interpretation of the remaining columns may depend on the transaction type.
        A full list of transaction types is available
        [from the FEC](http://www.fec.gov/finance/disclosure/metadata/DataDictionaryTransactionTypeCodes.shtml)
        . See also the
        [campaign finance methodology page](http://influenceexplorer.com/about/methodology/campaign_finance)
        for how transaction types are used in Influence Explorer. State records
        do not have transaction types.
    </dd>
    <dt>
        transaction_type_description
    </dt>
    <dd>
        A description of the transaction_type code, taken from the FEC descriptions
        [here](http://www.fec.gov/finance/disclosure/metadata/DataDictionaryTransactionTypeCodes.shtml)
        .
    </dd>
    <dt>
        filing_id
    </dt>
    <dd>
        Unique identifier for the actual filing with the FEC. State records do
        not yet have filing identifiers.
    </dd>
    <dt>
        is_amendment
    </dt>
    <dd>
        `TRUE` if transaction is an amendment to a previously reported transaction, otherwise `FALSE`.
    </dd>
    <dt>
        amount
    </dt>
    <dd>
        Amount of the transaction in US dollars.
    </dd>
    <dt>
        date
    </dt>
    <dd>
        Date of the transaction.
    </dd>
    <dt>
        contributor_name
    </dt>
    <dd>
        Typically indicates the name of the person or organization making the
        contribution. Exact meaning is dependent on transaction_type. For independent
        expenditures and electioneering cost this is the name of the committee
        making the expenditure.
    </dd>
    <dt>
        contributor_ext_id
    </dt>
    <dd>
        The NIMSP or CRP ID of the contributor, if an ID exists.
    </dd>
    <dt>
        contributor_type
    </dt>
    <dd>
        `I` for individual or `C` for PAC. NIMSP (state) records do not
        have a contributor type.
    </dd>
    <dt>
        contributor_occupation
    </dt>
    <dd>
        The self-reported occupation of the contributor.
    </dd>
    <dt>
        contributor_employer
    </dt>
    <dd>
        The self-reported employer of the contributor.
    </dd>
    <dt>
        contributor_gender
    </dt>
    <dd>
        `M` for male, `F` for female. Gender will only be found on
        CRP (federal) records.
    </dd>
    <dt>
        contributor_address
    </dt>
    <dd>
        The self-reported address of the contributor.
    </dd>
    <dt>
        contributor_city
    </dt>
    <dd>
        The self-reported city of the contributor.
    </dd>
    <dt>
        contributor_state
    </dt>
    <dd>
        The self-reported state of the contributor as the two-letter state abbreviation.
    </dd>
    <dt>
        contributor_zipcode
    </dt>
    <dd>
        The self-reported ZIPCode of the contributor.
    </dd>
    <dt>
        contributor_category
    </dt>
    <dd>
        The five character industry
        [category code](http://assets.transparencydata.org.s3.amazonaws.com/docs/catcodes.csv)
        of the contributor assigned by CRP or NIMSP.
    </dd>
    <dt>
        organization_name
    </dt>
    <dd>
        The name of the organization related to the contributor (employee, owner,
        spouse of owner, etc.). CRP or NIMSP standardized name.
    </dd>
    <dt>
        organization_ext_id
    </dt>
    <dd>
        The NIMSP or CRP ID of the organization, if an ID exists.
    </dd>
    <dt>
        parent_organization_name
    </dt>
    <dd>
        The name of the parent organization if one exists. CRP or NIMSP standardized
        name.
    </dd>
    <dt>
        parent_organization_ext_id
    </dt>
    <dd>
        The NIMSP or CRP ID of the parent organization, if an ID exists.
    </dd>
    <dt>
        recipient_name
    </dt>
    <dd>
        Typically indicates the name of the candidate or organization receiving
        the contribution. For independent expenditures and electioneering cost
        this is the name of the candidate that was targeted in the spending.
    </dd>
    <dt>
        recipient_ext_id
    </dt>
    <dd>
        The NIMSP or CRP ID of the recipient.
    </dd>
    <dt>
        recipient_party
    </dt>
    <dd>
        The political party to which the recipient belongs. `3` for
        third party, `D` for Democratic Party, `I` for independent,
        `R` for Republican Party, and `U` for unknown.
    </dd>
    <dt>
        recipient_type
    </dt>
    <dd>
        `C` for committees, `O` for organizations, `P` for politicians.
    </dd>
    <dt>
        recipient_category
    </dt>
    <dd>
        The five character industry category code of the recipient assigned by
        CRP or NIMSP. A full listing of categories and category orders can be found
        in catcodes.csv.
    </dd>
    <dt>
        recipient_category_order
    </dt>
    <dd>
        The three character industry code of the recipient assigned by CRP or
        NIMSP. A full listing of categories and category orders can be found in
        catcodes.csv.
    </dd>
    <dt>
        committee_name
    </dt>
    <dd>
        The name of the committee associated with the recipient of the contribution.
        This may be a parent committee or the election committee for the candidate.
    </dd>
    <dt>
        committee_ext_id
    </dt>
    <dd>
        The NIMSP or CRP ID of the committee.
    </dd>
    <dt>
        committee_party
    </dt>
    <dd>
        The political party to which the committee belongs.
        `3` for third party, `D` for Democratic Party, `I` for independent,
        `R` for Republican Party, and `U` for unknown.
    </dd>
    <dt>
        candidacy_status
    </dt>
    <dd>
        `TRUE` for general election, `FALSE` for lost in the primary or
        dropped out, `NULL` if never ran.
    </dd>
    <dt>
        district
    </dt>
    <dd>
        The district that the candidate represents, if there is one. The district
        is as the state abbreviation followed by the district number. For example:
        `CA-12`.
    </dd>
    <dt>
        seat
    </dt>
    <dd>
        <p>
            The type of office being sought by the candidate.
        </p>
        <table>
            <thead>
                <tr>
                    <th>Value</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>`federal:senate`</td>
                    <td>US Senate</td>
                </tr>
                <tr>
                    <td>`federal:house`</td>
                    <td>US House of Representatives</td>
                </tr>
                <tr>
                    <td>`federal:president`</td>
                    <td>US President</td>
                </tr>
                <tr>
                    <td>`state:upper`</td>
                    <td>upper chamber of state legislature</td>
                </tr>
                <tr>
                    <td>`state:lower`</td>
                    <td>lower chamber of state legislature</td>
                </tr>
                <tr>
                    <td>`state:governor`</td>
                    <td>state governor</td>
                </tr>
            </tbody>
        </table>
    </dd>
    <dt>
        seat_status
    </dt>
    <dd>
        `I` for incumbent, `O` for open. The value will be filled in
        as available in the source data.
    </dd>
    <dt>
        seat_result
    </dt>
    <dd>
        `W` for win, `L` for loss. The value will be filled in as
        available in the source data.
    </dd>
</dl>