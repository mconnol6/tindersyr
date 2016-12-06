/*$(function() {
    $('#upload_button').click(function() {
        var form_data = new FormData($('#upload_form')[0]);
        $.ajax({
            url: '/upload_picture',
            data: $('#upload_form').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(respones);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});*/
$(function() {
    $('#upload_button').click(function() {
        var form_data = new FormData($('#upload_form')[0]);
        $.ajax({
            url: '/upload_picture',
            data: form_data,
            type: 'POST',
            contentType: false,
            cache: false,
            processData: false,
            async: false,
            success: function(response) {
                console.log(respones);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});
