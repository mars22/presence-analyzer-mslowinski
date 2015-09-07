google.load("visualization", "1", {packages: ["corechart"], 'language': 'pl'});
(function ($, app) {
    'use strict';
    $(function () {
        function parseInterval(value) {
            var result = new Date(1, 1, 1);
            result.setMilliseconds(value * 1000);
            return result;
        }

        app.user_id_changed = function (selected_user, chart_div) {
            return $.getJSON(chart_div.data("api-url") + selected_user, function (result) {
                $.each(result, function (i, value) {
                    value[1] = parseInterval(value[1]);
                });
                var data = new google.visualization.DataTable(),
                    options = { hAxis: {title: 'Weekday'} },
                    formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'}),
                    chart = new google.visualization.ColumnChart(chart_div[0]);
                data.addColumn('string', 'Weekday');
                data.addColumn('datetime', 'Mean time (h:m:s)');
                data.addRows(result);
                formatter.format(data, 1);
                chart_div.show();
                chart.draw(data, options);
            });
        };
    });
})(jQuery, app);
