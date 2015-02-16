function selectDiagram(measure) {
	$.getJSON($SCRIPT_ROOT + '/_create_diagram', {
		diagram: measure
	}, function(data) {
		$("#distribution").show();
		updateDiagram(data.url);
		createDiagramInfo(data.average);

	});
	return false;
}

/**
 * A function that creates a request to server to initialize a diagram
 * showing the variance of average degree of graph over the time specified
 * by the user.
 */
function dynamicAnalysis() {
	$.getJSON($SCRIPT_ROOT + '/_dynamic_analysis', {
			time: $(".time-selector").slider().slider("value")
		}, function(data) {
			showDownloadBar();
			$("#path-over-time, #degree-over-time").show();
			updatePathOverTimeDiagram(data.pathInTime);
			updateDegreeOverTimeDiagram(data.degree);
	});
}

