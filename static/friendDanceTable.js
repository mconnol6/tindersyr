// global variables

var chosenFriend = '-1';
var chosenDance = '-1';

var usersFriends = {
	"names":[
		{"name":"Jack"}, 
		{"name":"Paul"},
		{"name":"Madelyn"}, 
		{"name":"Anna"},
		{"name":"Peter"}
	]
};

/*var userProfile = {
	"userInfo": [
		{
			"name": "Paul Dowling",
			"netID": "pdowlin8",
			"hometown": "Chicago, IL",
			"major": "computer science",
			"dorm": "Duncan",
			"year": "2017",
			"sex": "Male",
			"bio": "I love coding all the time. It's all I do! And I like cars."
		}

	]
};*/

var candidates = {
	"candidates": [
		{
			"name": "Person2",
			"netID": "person2",
			"hometown": "town2",
			"major": "computer science",
			"year": "2017",
			"sex": "male",
			"bio": "this is a bio about person 2"
		}

	]
};

var candidateIndex = 0;
var numCandidates = 0;




// server calling functions

$.makeRow = function (content) {
	var myRow = $('<tr style="width: 100%;">');
	var TableRow = '';
	TableRow += "<td style='width: 100%;'><h4>" + content + "</h4></td>";
	TableRow += "</tr>";
	$(myRow).append(TableRow);
	return ($(myRow));
};


$.displayFriends = function (mydata) {
	$.each(mydata, function (index, val) {
		$.each(val, function (index, blah) {
			$.each(blah, function (index, name) {
				var myRow = $.makeRow(name);
				console.log(name);
				$(myRow).appendTo("#friendTableBody");
			});
		});
	});
};

$.getCandidates = function(personBeingSetUp, dance) {
	// call database with that info, get the following json back
	candidates = {
		"candidates": [
			{
				"name": "Person4",
				"netID": "person4",
				"hometown": "town4",
				"major": "computer science",
				"year": "2017",
				"sex": "male",
				"bio": "this is a bio about person 4"
			},
			{
				"name": "Person5",
				"netID": "person5",
				"hometown": "town5",
				"major": "computer science",
				"year": "2017",
				"sex": "male",
				"bio": "this is a bio about person 5"
			},
			{
				"name": "Person1",
				"netID": "person1",
				"hometown": "town1",
				"major": "computer science",
				"year": "2017",
				"sex": "male",
				"bio": "this is a bio about person 1"
			},
			{
				"name": "Person3",
				"netID": "person3",
				"hometown": "town3",
				"major": "computer science",
				"year": "2017",
				"sex": "male",
				"bio": "this is a bio about person 3"
			},
			{
				"name": "Person6",
				"netID": "person6",
				"hometown": "town6",
				"major": "computer science",
				"year": "2017",
				"sex": "male",
				"bio": "this is a bio about person 6"
			}
				
		]
	}

	numCandidates = candidates["candidates"].length;
	console.log('there are', numCandidates, 'candidates');
	return candidates;
};




// document ready, click handlers

$( document ).ready(function() {


	// initialize
	var mydata = eval(usersFriends);
	$.displayFriends(mydata);
	
	$("#userNetID").text(userProfile["userInfo"][0]["netID"]);
	$("#userName").text(userProfile["userInfo"][0]["name"]);
	$("#userName2").text(userProfile["userInfo"][0]["name"]);


	$("#editProfileLink").click(function () {
		// initialize edit profile modal to the current stuff
		$("#editName").val(userProfile["userInfo"][0]["name"]);
		$("#editHometown").val(userProfile["userInfo"][0]["hometown"]);
		$("#editBio").val(userProfile["userInfo"][0]["bio"]);
		$("#editYear").val(userProfile["userInfo"][0]["year"]);
		$("#editSex").val(userProfile["userInfo"][0]["sex"]);
		$("#editDorm").val(userProfile["userInfo"][0]["dorm"]);
		$("#editMajor").val(userProfile["userInfo"][0]["major"]);

	});

	$("#saveProfileEdit").click(function () {
		var newName = $("#editName").val();
		var newHometown = $("#editHometown").val();
		var newBio = $("#editBio").val();
		var newYear = $("#editYear").val();
		var newSex = $("#editSex").val();
		var newDorm = $("#editDorm").val();
		var newMajor = $("#editMajor").val();
		setUserProfile(newName, newSex, newHometown, newDorm, newYear, newMajor, newBio);
	});


	function setUserProfile(name, sex, hometown, dorm, year, major, bio) {
		// PUT request to database here

		// update front-end user info
		userProfile["userInfo"][0]["name"] = name;
		userProfile["userInfo"][0]["bio"] = bio;
		userProfile["userInfo"][0]["hometown"] = hometown;
		userProfile["userInfo"][0]["year"] = year;
		userProfile["userInfo"][0]["sex"] = sex;
		userProfile["userInfo"][0]["dorm"] = dorm;
		userProfile["userInfo"][0]["major"] = major;

		console.log('user info is now', userProfile);
	};

	function setCandidateToIndex(candidateIndex) {

		if (candidateIndex >= numCandidates) {
			// out of candidates
			console.log('no more options!');
			$("#noMoreOptionsModal").modal("show");
			return;
		}

		var info = candidates["candidates"][candidateIndex];
		console.log('candidate', candidateIndex, 'is', info);
		$("#candidateName").text(info["name"]);
		$("#candidateBio").text(info["bio"]);
		$("#candidateYear").text(info["year"]);
		$("#candidateHometown").text(info["hometown"]);
		$("#candidateDorm").text(info["dorm"]);
		$("#candidateMajor").text(info["major"]);

	};

	function addFriend(name, netID, sex, hometown, dorm, year, major, bio) {
		// POST request for this new friend

		// add new friend to friend table
		var myRow = $.makeRow(name);
		$(myRow).appendTo("#friendTableBody");
	};

	$("#addFriendSave").click( function() {
		var name = $("#friendName").val();
		var netID = $("#friendNetID").val();
		var bio = $("#friendBio").val();
		var hometown = $("#friendHometown").val();
		var sex = $("#friendSex").val();
		var major = $("#friendMajor").val();
		var dorm = $("#friendDorm").val();
		var year = $("#friendYear").val();

		addFriend(name, netID, sex, hometown, dorm, year, major, bio);

		$("#friendName").val('');
		$("#friendNetID").val('');
		$("#friendBio").val('');
		$("#friendHometown").val('');
		$("#friendSex").val('');
		$("#friendMajor").val('');
		$("#friendDorm").val('');
		$("#friendYear").val('');
	});

	
	
	$("#friendTableBody").on('click', 'tr', function() {
		console.log($(this).text());
		chosenFriend = $(this).text();
		var selected = $(this).hasClass("highlight");
		$("#personBeingSetUp").text(chosenFriend);
		$("#friendTable tr").removeClass("highlight");

		if(!selected)
			$(this).addClass("highlight");
	});

	$("#danceTable tr").click(function() {
		console.log($(this).text());
		chosenDance = $(this).text();
		$("#dance").text(chosenDance);
		var selected = $(this).hasClass("highlight");
		$("#danceTable tr").removeClass("highlight");
		if(!selected)
			$(this).addClass("highlight");
	});

	// start swiping
	$("#go").click(function() {
		console.log("pressed go");

		// change divs visibility
		$("#choices").css("visibility", "hidden");
		$("#choices").css("height", "0px");
		$("#syrInfo").css("visibility", "visible");
		$("#syrInfo").css("height", "900px");
		
		// get candidates for this friend/dance
		candidates = $.getCandidates("mnelso12", "trumpetSYR");
		console.log('candidates:', candidates);	

	});

	$("#backToChooseFriendAndDance").click(function() {
		console.log("pressed back");
		// change divs visibility
		$("#choices").css("visibility", "visible");
		$("#choices").css("height", "1000px");
		$("#syrInfo").css("visibility", "hidden");
		$("#syrInfo").css("height", "0px");
	});


	$("#yay").click(function() {
		console.log("pressed yay");
		candidateIndex += 1;
		setCandidateToIndex(candidateIndex);
	});

	$("#nay").click(function() {
		console.log("pressed nay");
		candidateIndex += 1;
		setCandidateToIndex(candidateIndex);
	});

	$("#newFriendAndDance").click(function() {
		console.log("out of candidates, pick new friend and dance");
		// change divs visibility
		$("#choices").css("visibility", "visible");
		$("#choices").css("height", "1000px");
		$("#syrInfo").css("visibility", "hidden");
		$("#syrInfo").css("height", "0px");
	});


});
