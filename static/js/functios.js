function checkIfUsernameExists() {
	if($('#user').val() == "")
	   $('#check_username').text('You have to enter a username');
	else {
		$.getJSON($SCRIPT_ROOT + '/_check_user', {
			username: $('#user').val()
		}, function(data) {
			$('#check_username').text(data);
		});
		return false;
	}
		
}

function checkPasswords() {
	var password1 = $('#new_pass').val();
	var password2 = $('#new_pass2').val();
	matches = false;
	if(password1 == password2)
		if(password1.length >= 6) {
			$('#check_passwords').text("Your password matches");
			matches = true;
		} else
			$('#check_passwords').text("Password must contain at least 6 characters");
	else
		$('#check_passwords').text("Your passowrd doesn't match");
	return matches;	
}

function createAccount() {
	var message2 = 'Your username is accepted!'
	checkIfUsernameExists()
	var checkUsername = $('#check_username').text();
	var matches = checkPasswords();
	if(checkUsername != message2 || !matches)
		alert("Error! New account can't be created. Please check all fields again");
	else{
		$.getJSON($SCRIPT_ROOT + '/_new_account', {
			username: $('#user').val(),
			password: $('#new_pass').val()
		}, function(data) {
			
			alert("Your new account created successfully! Now, you can login and analyze graphs!")
		});
	}
}

function hideElements() {
	if($('#fs2').is(':visible'))
		$('#fs2').hide();
	else
		$('#fs2').show();
}
