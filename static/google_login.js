// Controls google login to app.
function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
      auth2.disconnect();
      console.log('User signed out.');
    });
  }

function onSignIn(googleUser) {
  var profile = googleUser.getBasicProfile();
  //console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
  //console.log('Name: ' + profile.getName());
  //console.log('Image URL: ' + profile.getImageUrl());
  //console.log('Email: ' + profile.getEmail());

  var email_list = profile.getEmail().split("@");
  
  if (email_list[1] != 'nd.edu') {
      $('#error').html('Log out of this Google account and sign in with an nd.edu address.');
      return;
  }

  // The ID token you need to pass to your backend:
  sendEmail(profile.getEmail());
  //console.log("Finished");
}

function sendEmail(email) {
  $.ajax({
    url: '/login',
    data: email,
    type: 'POST',
    success: function(response) {
        if (response == 'yes') {
            window.location.replace('/index')
        } else {
            window.location.replace('/signup_form')
        }
    },
    error: function(error) {
      console.log(error);
    }
  });
}
