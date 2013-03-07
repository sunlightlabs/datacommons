## Earmarks Schema

<style>
    dd{ clear: left; margin-bottom: 1em; }
</style>

<dl>
    <dt>
        fiscal_year
    </dt>
    <dd>
        The fiscal year for the bill in which the earmark appears.
    </dd>
    <dt>
        final_amount
    </dt>
    <dd>
        The earmark amount in the final version of the bill.
    </dd>
    <dt>
        budget_amount
    </dt>
    <dd>
        The earmark amount in the President's budget proposal.
    </dd>
    <dt>
        house_amount
    </dt>
    <dd>
        The earmark amount in the version of the bill passed by the House.
    </dd>
    <dt>
        senate_amount
    </dt>
    <dd>
        The earmark amount in the version of the bill passed by the Senate.
    </dd>
    <dt>
        omni_amount
    </dt>
    <dd>
        The earmark amount in the omnibus appropriations bill.
    </dd>
    <dt>
        bill, bill_section, bill_subsection
    </dt>
    <dd>
        The bill, section and subsection where the earmark appears.
    </dd>
    <dt>
        description
    </dt>
    <dd>
        The earmark description.
    </dd>
    <dt>
        notes
    </dt>
    <dd>
        Notes added by Taxpayers for Common Sense.
    </dd>
    <dt>
        presidential
    </dt>
    <dd>
        <p>
            Presidential earmarks are earmarks that appear in the President's initial
            budget proposal.
        </p>
        <table>
            <thead>
                <tr>
                    <th>Value</th>
                    <th>Meaning</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>blank</td>
                    <td>Not in the President's budget.</td>
                </tr>
                <tr>
                    <td>`p`</td>
                    <td>Included in the President's budget and disclosed by congress.</td>
                </tr>
                <tr>
                    <td>`u`</td>
                    <td>Included in the President's budget and not disclosed by congress.</td>
                </tr>
                <tr>
                    <td>`m`</td>
                    <td>Included in the President's budget and sponsored by members.</td>
                </tr>
                <tr>
                    <td>`j`</td>
                    <td>Included at the request of the judiciary.</td>
                </tr>
            </tbody>
        </table>
    </dd>
    <dt>
        undisclosed
    </dt>
    <dd>
        <p>
            Taxpayers for Common Sense's determination of whether the earmarks was
            disclosed by congress. Undisclosed earmarks are found by reading the bill
            text.
        </p>
        <table>
            <thead>
                <tr>
                    <th>Value</th>
                    <th>Meaning</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>blank</td>
                    <td>Disclosed in congressional earmark reports.</td>
                </tr>
                <tr>
                    <td>`u`</td>
                    <td>Not disclosed by congress but found in bill text.</td>
                </tr>
                <tr>
                    <td>`p`</td>
                    <td>Not disclosed and in President's budget.</td>
                </tr>
                <tr>
                    <td>`o`</td>
                    <td>Disclosed Operations &amp; Maintenance earmark.</td>
                </tr>
                <tr>
                    <td>`m`</td>
                    <td>Undisclosed Operations &amp; Maintenance earmark.</td>
                </tr>
            </tbody>
        </table>
    </dd>
    <dt>
        members
    </dt>
    <dd>
        The members that sponsored the earmark. Taxpayers for Common Sense lists
        the members by last name, state and party. We have attempted to expand
        these to full names, where possible. Due to formatting irregularities,
        state, party or full name are sometimes missing.
    </dd>
    <dt>
        location
    </dt>
    <dd>
        The city and states where the earmark will be spent, when known.
    </dd>
    <dt>
        recipients
    </dt>
    <dd>
        The organization that will receive the earmark, when known.
    </dd>
</dl>