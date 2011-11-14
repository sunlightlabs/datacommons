$().ready(function() {

    TD.BundlingFilter = new TD.DataFilter();

    TD.BundlingFilter.path = 'contributions/bundled';

    TD.BundlingFilter.row_content = function(row) {
        var bundler = TD.Utils.coalesce(new Array(row.standardized_lobbyist_name, row.bundler_name))
        if (row.bundler_employer) {
            bundler += ', ' + TD.Utils.coalesce(new Array(row.standardized_firm_name, row.bundler_employer))
        }

        var content = ''
        content += '<td class="recipient_name">' + TD.Utils.coalesce(new Array(row.standardized_recipient_name, row.committee_name)) + '</td>';
        content += '<td class="lobbyist_name">' + bundler + '</td>';
        content += '<td class="amount">$' + TD.Utils.currencyFormat(TD.Utils.coalesce(new Array(row.semi_annual_amount, row.period_amount))) + '</td>'
        content += '<td class="coverage_period">' + row.start_date + ' to ' + row.end_date + '</td>';

        return content;
    }

    TD.BundlingFilter.init = function() {

        TD.BundlingFilter.registerFilter({
            name: 'recipient_name',
            label: 'Recipient',
            help: 'Name of the politician or committee which received the bundled contribution',
            field: TD.DataFilter.TextField,
            allowMultipleFields: true
        });

        TD.BundlingFilter.registerFilter({
            name: 'lobbyist_name',
            label: 'Lobbyist',
            help: 'Lobbyist or lobbying firm who bundled the contributions',
            field: TD.DataFilter.TextField,
            allowMultipleFields: true
        });

        var anchor = TD.HashMonitor.getAnchor();
        if (anchor === undefined) {
            this.loadHash();
        }

    };

});
