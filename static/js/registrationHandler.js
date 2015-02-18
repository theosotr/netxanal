/**
 * Takes user's input and if they are
 * validated, it sends them to the
 * CheckInputServlet for editing.
 */
function checkInputIfExists(input) {
	if (acceptInput(input)) {
		$.getJSON($SCRIPT_ROOT + '/_check_user', {
			value: $('#' + input).val(),
			inputType: input
		}, function(data) {
			$('#accept' + input).text(data);
		});
		return false;
	}
}

/**
 * Takes user's input and validates them
 */
function acceptInput(input) {
	var accepted = true;
	if(input == "username") {
		if($("#" + input).val().length < 3) {
			$("#accept" + input).text("Username must contain at least 3 characters");
			accepted = false;
		}
	} else {
		var words = $("#" + input).val().split("@");
		if(words.length == 1 || words.length > 2) {
			$('#accept' + input).text("Given value is not accepted.");
			accepted = false;
		} else {
			var words2 = words[1].split(".");
			if(words2.length == 1 || words2.length > 2) {
				$('#accept' + input).text("Given value is not accepted.");
				accepted = false;
			}
		}
	}

	return accepted;
}

/**
 * Checks if the two passwords are same and have more
 * than 6 characters. If not it doesn't accept them.
 */
function verifyPasswords() {
	var password1 = $('#pswrd1').val();
	var password2 = $('#pswrd2').val();
	var accepted = false;
	if(password1 == password2)
		if(password1.length >= 6) {
			$('#acceptPswrd').text("Passwords match.");
			accepted = true;
		} else
			$('#acceptPswrd').text("Password must contain at least 6 characters");
	else
	if(password1 == "")
		$('#acceptPswrd').text("Give a password. This field is required.");
	else
		$('#acceptPswrd').text("Passwords do not match.");
	return accepted;
}

/**
 *  Takes user's credentials it validates them
 *  and if they are, it sends them to the User class
 *  for creating a new user.
 */
function createAccount() {
	var firstName = $('#firstName').val();
	var surname = $('#surname').val();
	checkInputIfExists('username');
	checkInputIfExists('email');
	var usernameAccepted = $('#acceptusername').text();
	var emailAccepted = $('#acceptemail').text();
	var passwordAccepted = verifyPasswords();
	if(firstName == "" || surname == ""
		|| usernameAccepted != "Your username is accepted!"
		|| emailAccepted != "Your email is accepted!"
		|| !passwordAccepted) {

		alert("Your registration cannot be completed! Please, check again fields");
	} else {
		$.getJSON($SCRIPT_ROOT + '/_new_account', {
			name: firstName,
			lastName: surname,
			username: $('#username').val(),
			email: $('#email').val(),
			password: $('#pswrd1').val()
		}, function(data) {
			alert(data);
			window.location.reload(true);
        });
	}
}
