function set_hidden_inputs() {
    $('#name').val($('#name_first').val());    
    $('#netid').val($('#netid_first').val());    
    $('#dorm').val($('#dorm_first').val());    
}

function set_hidden_inputs2() {
    $('#year').val($('#year_first').val());    
    $('#bio').val($('#bio_first').val());    
    $('#hometown').val($('#hometown_first').val());    
    $('#gender').val($('#gender_first').val());    
    $('#interested_in').val($('#interested_in_first').val());    
    $('#major').val($('#major_first').val());    
}


var interestArr = [];

$( document ).ready(function() {

	// clear all interests
	$("#clear").on("click", function () {
		console.log("clearing interests");
		interestArr = [];
		$("#interestList").text("");
	});

	// click handler for all interest buttons
	$("#interests").on("click", "button", function () {
		console.log('click');
		console.log($(this).text());	

		// if not already in interest list, add it
		if (interestArr.indexOf($(this).text()) < 0) {
			var newInterest = $(this).text();
			interestArr.push(newInterest);
			var oldInterestList = $("#interestList").text();
			if (interestArr.length > 1) { // 1 because already added newst interest
				console.log('num interests', interestArr.length);

				oldInterestList += ', ';
			}
			oldInterestList += newInterest;
			$("#interestList").text(oldInterestList);
		}
	});

});
