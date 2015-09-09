var app = {
    user_id_changed: function (selected_user, chart_div) {}
};
(function ($, app) {
    'use strict';
    $(function () {
        $("li > a[href='" + window.location.pathname + "']").parent().addClass("selected");
        var loading = $('#loading'),
            chart_div = $('#chart_div'),
            dropdown = $("#user_id");

        $.getJSON(dropdown.data("api-url"), function (result) {
            $.each(result, function (i, item) {
                dropdown.append($("<option />").val(item.user_id).text(item.name));
            });
            dropdown.show();
            loading.hide();
        });

        $('#user_id').change(function () {
            var selected_user = $("#user_id").val();
            if (selected_user) {
                loading.show();
                chart_div.hide();
                app.user_id_changed(selected_user, chart_div).complete(function () {
                    loading.hide();
                });
            }
        });
    });
})(jQuery, app);
