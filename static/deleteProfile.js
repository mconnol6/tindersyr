function deleteProfile() {
    $.ajax({
        url: '/delete_account',
        type: 'POST',
        success: function(response) {
            window.location.replace('/login')
        },
        error: function(error) {
            console.log(error);
        }
    });
}
