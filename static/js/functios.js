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

function rankingWay(option) {
	
	if(option == 'colorRanking') {
		$('#colorRanking').show();
		$('#sizeRanking').hide();
	} else if(option == 'sizeRanking') {
		$('#colorRanking').hide();
		$('#sizeRanking').show();
	} else {
		$('#colorRanking').show();
		$('#sizeRanking').show();
	}
}


function selectTypeOfInfo() {
	if($("#nodes").is(":visible")) {
		$("#nodes").hide();
		$("#edges").show();
		$("#selectEdge").show();
		$("#selectColumn").hide();
		$("#selectWay").attr("onchange", "sortEdges()");
		$("#displayInfo").attr("value", "Nodes");
	} else {
		$("#nodes").show();
		$("#edges").hide();
		$("#selectEdge").hide();
		$("#selectColumn").show();
		$("#selectWay").attr("onchange", "sortNodes()");
		$("#displayInfo").attr("value", "Edges");
		
	}
}

function deleteProject() {
	$.getJSON($SCRIPT_ROOT + '/_delete_project', {
		project: $("input[name=project]:checked").val()
		
	}, function(data) {
		window.location.reload(true); 
		
	});
}

function sendResponse(save) {
	window.returnValue = save;
	window.close();
}

function selectGraphModel() {
	var graphModel = $("#model").val();
	if(graphModel == "erdos" || graphModel == "binomial") {
		$("#modelDescription").text("Chooses each of the possible edges with a " +
				"given probability.");
		$("#parameters").empty();
		$("#parameters").append("Number of nodes: <input name = 'nodes' " +
				"type = 'text'/><br>" +
				"probability of edge creation: <input name = 'probability' " +
				"type = 'text'/><br>" + 
				"Graph type: <input type = 'radio' name = 'graphtype' value = " +
				"'Undirected'>Undirected<input type = 'radio' name = 'graphtype' " +
				"value = 'Directed'>Directed");
	} else if(graphModel == "watts_strogatz") {
		$("#modelDescription").text("Generates a graph which has similar " +
				"characteristics with small-world netowrks");
		$("#parameters").empty();
		$("#parameters").append("Number of nodes: <input name = 'nodes' " +
				"type = 'text'/><br>" +
				"probability of edge creation: <input name = 'probability' " +
				"type = 'text'/><br>" +
				"Number of edges to the nearest neighbors" +
				"<input name = 'edges' type = 'text'><br>Is fully connected: " +
				"<input type = 'radio' name = 'isConnected' value = 'Yes'>Yes" +
				"<input type = 'radio' name = 'isConnected' value = 'No'>No<br>");
	} else if(graphModel == "regular") {
		$("#modelDescription").text("Generates a graph whose nodes have " +
				"the given degree");
		$("#parameters").empty();
		$("#parameters").append("Number of nodes: <input name = 'nodes' " +
				"type = 'text'/><br>" +
				"Degree of each node: <input name = 'degree' type = 'text'/>");
	} else if(graphModel == "random") {
		$("#modelDescription").text("Generates a graph with both number of " +
		"nodes and number of edges given by user");
		$("#parameters").empty();
		$("#parameters").append("Number of nodes: <input name = 'nodes' " +
		"type = 'text'/><br>" +
		"Number of edges: <input name = 'edges' type = 'text'/><br>" +
		"Graph type: <input type = 'radio' name = 'graphtype' value = " +
		"'Undirected'>Undirected<input type = 'radio' name = 'graphtype' " +
		"value = 'Directed'>Directed");
	} else if(graphModel == "barabasi") {
		$("#modelDescription").text("Generates a growing graph based on" +
		"preferential attachment model.");
		$("#parameters").empty();
		$("#parameters").append("Number of nodes: <input name = 'nodes' " +
		"type = 'text'/><br>" +
		"Graph type: <input type = 'radio' name = 'graphtype' value = " +
		"'Undirected'>Undirected<input type = 'radio' name = 'graphtype' " +
		"value = 'Directed'>Directed");
	}

}