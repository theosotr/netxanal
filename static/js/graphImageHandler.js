function findPaths() {
	$.getJSON($SCRIPT_ROOT + '/_find_paths', {
		source: $('#source').val(),
		target: $('#target').val(),
		pathType: $("#path-type input[name='pathType']:checked").val(),
		calculationWay: $('#pathCalculation').val()
	}, function(data) {
		if (jQuery.isEmptyObject(data)) alertPathNotExists();
		else {
			updateGraphImage(data.url);
			alertPath(data.pathSequence, data.pathLength);
		}
	});
	return false;
}

function updateImage(componentToUpdate, color) {
	var newValue = getUpdatedValue(componentToUpdate, color);
    $.getJSON($SCRIPT_ROOT + '/_update_image', {
		componentToUpdate: componentToUpdate,
        updatedValue: newValue
	}, function(data) {
		updateGraphImage(data);
	});
}

function findCommunities(level) {
    $.getJSON($SCRIPT_ROOT + '/_find_communities', {
		level: level
	}, function(data) {
		updateGraphImage(data.url);
		showCommunities(data.listOfCommunities, data.levels);
	});
}

function findCliques() {
	$.getJSON($SCRIPT_ROOT + '/_find_cliques', {
	}, function(data) {
		showCliques(data);
	});
}

function rankNodes() {
	var rankingWay = $("#rankings").find("input[type=radio]:checked").val();
	$.getJSON($SCRIPT_ROOT + '/_rank_nodes', {
		colorMeasure: $('#colorNodes').val(),
		sizeMeasure: $('#sizeNodes').val(),
		colors: $('#color-map').val(),
		rankingWay: rankingWay
	}, function(data) {
		if(rankingWay == 'sizeRanking')
			$('#colorbase').hide();
		else
			$('#colorbase').show();
		updateGraphImage(data[0]);
		$('#colorbase').attr('src', data[1]);

	});
	return false;
}

function getUpdatedValue(componentToUpdate, color) {
	var newValue;
	var elementToUpdate = $("#update-" + componentToUpdate);
	switch (componentToUpdate) {
		case "node_color":case "edge_color":case "font_color":
			newValue = color;
			break;
		case "node_size":case "edge_width":case "font_size":
			newValue = elementToUpdate.slider("value");
			break;
		case "node_shape":case "edge_labels":
			newValue = elementToUpdate.find("input[type=radio]:checked").val();
			break;
		default:
			newValue = elementToUpdate.val();
			break;
	}
	return newValue;
}