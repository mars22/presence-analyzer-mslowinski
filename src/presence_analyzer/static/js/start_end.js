google.load("visualization", "1", {packages: ["corechart", "timeline"], 'language': 'pl'});
(function ($, app) {
    'use strict';
    $(function () {
        function convertTimeToDate(time) {
            return new Date("1899-12-31 " + time);
        }

        app.user_id_changed = function (selected_user, chart_div) {
            return $.getJSON(chart_div.data("api-url") + selected_user, function (result) {
                var data = new google.visualization.DataTable(),
                    convertedResults = [],
                    options = { hAxis: {title: 'Weekday'}},
                    formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'}),
                    chart = new google.visualization.Timeline(chart_div[0]);
                data.addColumn('string', 'Weekday');
                data.addColumn({ type: 'datetime', id: 'Start' });
                data.addColumn({ type: 'datetime', id: 'End' });
                $.each(result, function (i, item) {
                    var day = item[0],
                        start = convertTimeToDate(item[1]),
                        end = convertTimeToDate(item[2]);
                    convertedResults.push([day, start, end]);
                });
                data.addRows(convertedResults);
                formatter.format(data, 1);
                formatter.format(data, 2);
                chart_div.show();
                chart.draw(data, options);
            });
        };
    });
})(jQuery, app);
