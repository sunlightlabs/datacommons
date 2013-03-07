## Federal Lobbying Data Schema

<style>
    dd{ clear: left; margin-bottom: 1em; }
</style>

### Lobbying
    
<dl>
    <dt>
        transaction_id
    </dt>
    <dd>
        The registration ID assigned by the Senate Office of Public Records.
    </dd>
    <dt>
        transaction_type
    </dt>
    <dd>
        The type of filing as reported by the Senate Office of Public Records.
        <http://assets.transparencydata.org.s3.amazonaws.com/docs/transaction_types-20100402.csv>
    </dd>
    <dt>
        transaction_type_desc
    </dt>
    <dd>
        Readable description of the transaction_type.
    </dd>
    <dt>
        year
    </dt>
    <dd>
        The year in which the registration was filed. Valid years are 1998-2009.
    </dd>
    <dt>
        filing_type
    </dt>
    <dd>
        <p>Type of filing as identified by CRP. CRP recommends the following rules
           be used:
        </p>
        <ul>
            <li>
                Do not total e records unless they are larger than the associated s record.
            </li>
            <li>
                Count c records in both total and industry when `filing_included_nsfs` is
                `n`. Don't count it in total or industry when `filing_included_nsfs` is `y`.
            </li>
            <li>
                Count b records in both total and industry when `filing_included_nsfs` is `n`.
                Exclude from total and include in industry but subtract it from the
                total of the parent when `filing_included_nsfs` is `y`.
            </li>
        </ul>
        <table>
            <thead>
                <tr>
                    <th>Code</th>
                    <th>Meaning</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>`n`</td>
                    <td>non self filer parent</td>
                </tr>
                <tr>
                    <td>`m`</td>
                    <td>non self filer subsidiary for a non self filer parent</td>
                </tr>
                <tr>
                    <td>`x`</td>
                    <td>self filer subsidiary for a non self filer parent</td>
                </tr>
                <tr>
                    <td>`p`</td>
                    <td>self filer parent</td>
                </tr>
                <tr>
                    <td>`i`</td>
                    <td>non self filer for a self filer parent that has same catorder as the parent</td>
                </tr>
                <tr>
                    <td>`s`</td>
                    <td>self filer subsidiary for a self filer parent</td>
                </tr>
                <tr>
                    <td>`e`</td>
                    <td>non self filer subsidiary for a self file subsidiary</td>
                </tr>
                <tr>
                    <td>`c`</td>
                    <td>non self filer subsidiary for a self filer parent with same catorder</td>
                </tr>
                <tr>
                    <td>`b`</td>
                    <td>non self filer subsidiary for a self filer parent that has different catorder</td>
                </tr>
            </tbody>
        </table>
    </dd>
    <dt>
        amount
    </dt>
    <dd>
        The amount spent on lobbying in US dollars.
    </dd>
    <dt>
        registrant_name
    </dt>
    <dd>
        Name of the person or organization filing the lobbyist registration. This
        is typically the firm that employs the lobbyists. Use the registrant_is_firm
        field to filter on firms v. individuals.
    </dd>
    <dt>
        registrant_is_firm
    </dt>
    <dd>
        `true` if registrant is a lobbying firm.
    </dd>
    <dt>
        client_name
    </dt>
    <dd>
        Name of the client for which the lobbyist is working.
    </dd>
    <dt>
        client_category
    </dt>
    <dd>
        The five character industry category code of the client assigned by CRP.
        <http://assets.transparencydata.org.s3.amazonaws.com/docs/catcodes-20100402.csv>
    </dd>
    <dt>
        client_ext_id
    </dt>
    <dd>
        CRP ID of the client if one exists.
    </dd>
    <dt>
        client_parent_name
    </dt>
    <dd>
        Name of the parent organization of the client.
    </dd>
</dl>

---

### Lobbyists

<dl>
    <dt>
        lobbyists.lobbyist_name
    </dt>
    <dd>
        Name of the lobbyist involved in the lobbying activity.
    </dd>
    <dt>
        lobbyists.lobbyist_ext_id
    </dt>
    <dd>
        Lobbyist ID assigned by CRP.
    </dd>
    <dt>
        lobbyists.candidate_ext_id
    </dt>
    <dd>
        Candidate ID, if the lobbyist was ever a candidate, assigned by CRP.
    </dd>
    <dt>
        lobbyists.government_position
    </dt>
    <dd>
        Position in the federal government if the lobbyist even held one.
    </dd>
    <dt>
        lobbyists.member_of_congress
    </dt>
    <dd>
        `true` if the lobbyist was ever a member of Congress.
    </dd>
</dl>

---

### Issues

<dl>
    <dt>
        issues.year
    </dt>
    <dd>
        The year in which the registration was filed. Valid years are 1998-2009.
    </dd>
    <dt>
        issues.general_issue_code
    </dt>
    <dd>
        The code that represents the issue on which the lobbying was conducted.
    </dd>
    <dt>
        issues.general_issue
    </dt>
    <dd>
        The name of the issue on which the lobbying was conducted.
    </dd>
    <dt>
        issues.specific_issue
    </dt>
    <dd>
        A description of the specific lobbying.
    </dd>
</dl>

---

### Agencies

<dl>
    <dt>
        agencies.agency_name
    </dt>
    <dd>
        The name of the federal agency that was lobbied.
    </dd>
    <dt>
        agencies.agency_ext_id
    </dt>
    <dd>
        The CRP ID of the agency that was lobbied.
    </dd>
</dl>
