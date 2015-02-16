$(function() {
    $("#nodes").tablesorter();
    $("#edges").tablesorter({
        sortList: [[0,0],[1,0], [2, 0], [3, 0]]
    });
});

function saveProject(graphName, save) {
    $.getJSON($SCRIPT_ROOT + '/_save_project', {
        project: graphName,
        saveAction: save
    }, function(data) {
        if(data) {
            saveDialog.dialog("close");
            saveCompleted.dialog("open");
        } else {
            setGraphName(graphName);
            overwriteForm.dialog("open");
        }
    });
}

function deleteProject() {
	$.getJSON($SCRIPT_ROOT + '/_delete_project', {
		project: window.project
	}, function() {
		deleteProjectFromPage();
	});
}