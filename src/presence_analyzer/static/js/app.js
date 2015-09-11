var app = {
    user_id_changed: function (selected_user, chart_div) {}
};
(function ($, app) {
    'use strict';
    $(function () {
        $("li > a[href='" + window.location.pathname + "']").parent().addClass("selected");
        var loading = $('#loading'),
            chart_div = $('#chart_div'),
            dropdown = $("#user_id"),
            no_data = $("#no_data"),
            avatar = $("#avatar");

        $.getJSON(dropdown.data("api-url"), function (result) {
            $.each(result, function (i, item) {
                dropdown.append($("<option />")
                    .val(item.user_id)
                    .text(item.name)
                    .attr("data-avatar-url", item.avatar_url));
            });
            dropdown.show();
            loading.hide();
        });

        $('#user_id').change(function () {
            var selected_user = $(this).find(":selected"),
                user_id = selected_user.val(),
                avatar_url = selected_user.data('avatar-url');
            if (user_id) {
                loading.show();
                chart_div.hide();
                no_data.hide();
                avatar.hide();
                app.user_id_changed(user_id, chart_div)
                    .fail(function () {
                        no_data.show();
                    })
                    .complete(function () {
                        loading.hide();
                        avatar.attr("src", avatar_url);
                        avatar.show();
                    });
            }
        });
    });
})(jQuery, app);
