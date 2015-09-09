google.load("visualization", "1", {packages: ["corechart"], 'language': 'en'});
(function ($, app) {
    'use strict';
    $(function () {
        app.user_id_changed = function (selected_user, chart_div) {
           return $.getJSON(chart_div.data("api-url") + selected_user, function (result) {
                var data = google.visualization.arrayToDataTable(result),
                    options = {},
                    chart = new google.visualization.PieChart(chart_div[0]);
                chart_div.show();
                chart.draw(data, options);
            });
        };
    });
})(jQuery, app);
