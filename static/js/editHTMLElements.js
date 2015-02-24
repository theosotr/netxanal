function updateGraphImage(url) {
    $("#graphImage").find("img").attr("src", url);
}

function alertPath(pathSequence, pathLength) {
    removePathSequence();
    var source = $("#source").val();
    var target = $("#target").val();
    var pathInfo = $("#pathInfo");
    pathInfo.append("<div id='pathSequence' class='ui-state-highlight ui-corner-all' " +
        "style='margin-top: 20px; padding: 0 .7em;'>" +
        "<p><span class='ui-icon ui-icon-info' " +
        "style='float: left; margin-right: .3em;'></span>" +
        "<b>" + pathSequence.length + " path(s) are detected!</b><br></div>");
    var path = $("#pathSequence");
    for (var i = 0; i < pathSequence.length; i ++) {
        var counter = i + 1;
        path.append("<b>Path " + counter + " sequence: </b>" +
            pathSequence[i] + "<br>");
    }
    path.append("<b>Path length: </b>" + pathLength);
}

function alertPathNotExists() {
    removePathSequence();
    var source = $("#source").val();
    var target = $("#target").val();
    $("#pathInfo").append("<div class='ui-state-error ui-corner-all' " +
        "style='margin-top: 20px; padding: 0 .7em;'>" +
        "<p><span class='ui-icon ui-icon-info' " +
        "style='float: left; margin-right: .3em;'></span>" +
        "<b>Warning: </b>There is no path between source node: " + source +
        " and target node: " + target);
}

function removePathSequence() {
    $("#pathInfo").empty();
}

function showCommunities(listOfCommunities, levels) {
    removeCommunities();
    var communities = $("#communitiesInfo");
    communities.append("<p><span class='ui-icon ui-icon-alert' " +
        "style='float: left; margin-right: .3em;'></span>" +
        "<strong>" + levels + " Levels of communities " +
        "are detected!</strong></p>");
    if (listOfCommunities.length > 1) {
        communities.append("<label id='tooltip' for='level' " +
        "title='Lower level means that fewer communities are" +
        "detected with more components on them.'>Select level: </label>" +
        "<select id = 'level'></select><br><br><br>");
        selectLevelOfCommunities(levels);
        $("#level").selectmenu({
            change: function(event) {
                event.preventDefault();
                findCommunities(this.value);
            }
        });
    }
    for (var i = 0; i < listOfCommunities.length; i++) {
        var counter= i + 1;
        communities.append("<b>Community: " + counter + " </b>&nbsp;"
            + listOfCommunities[i] + "<br>");
    }
}

function showCliques(cliques) {
    removeCliques();
    var cliquesInfo = $("#cliquesInfo");
    cliquesInfo.append("<div class='ui-state-highlight ui-corner-all' " +
        "style='margin-top: 20px; padding: 0 .7em;'><p id = 'cliqueList'><span " +
        "class='ui-icon ui-icon-info' style='float: left; margin-right: .3em;'>" +
        "</span><b>" + cliques.length + " Cliques are detected.</b><br></p></div>");
    for (var i = 0; i < cliques.length; i++) {
        var counter = i + 1;
        cliquesInfo.find("p").append("Clique " + counter + ": " + cliques[i] + "<br>");
    }
}

function removeCommunities() {
    $("#communitiesInfo").empty();
}

function removeCliques() {
    $("#cliquesInfo").empty();
}

function emptyLevelCommunitySelection() {
    $("#level").empty();
}

function selectLevelOfCommunities(levels) {
    emptyLevelCommunitySelection();
    var levelSelection = $("#level");
    for (var i = 1; i <= levels; i++)
        levelSelection.append("<option value=" + i + ">Level " + i + "</option>");
}

function changeRankingWay(rankingWay) {
    var sizeOptions = $("#sizeRanking");
    var colorOptions = $("#colorRanking");
    switch (rankingWay) {
        case "color":
            sizeOptions.hide();
            colorOptions.show();
            break;
        case "size":
            sizeOptions.show();
            colorOptions.hide();
            break;
        default :
            sizeOptions.show();
            colorOptions.show();
            break;
    }
}

function createWarningMessage(message) {
    removeWarningMessage();
    $("#save-form").find("p").after("<div id='warning' class='ui-corner-all " +
        "ui-state-error'><p><span class='ui-icon ui-icon-alert'></span>" +
        "<b>" + message + "</b> </p>");
}

function removeWarningMessage() {
    $("#warning").remove();
}

function setGraphName(graphName) {
    $("#graphName").text(graphName);
}

function removeDiagramInfo() {
    $("#average").remove();
}

function createDiagramInfo(average) {
    removeDiagramInfo();
    $("#diagramInfo").show();
    $("#diagramInfo ").find("div").prepend("<p id='average'><span " +
        "class='ui-icon ui-icon-info' style='float: " +
        "left; margin-right: .3em;'></span><b>Average value: </b>" + average +
        "</p>");
}

function updateDiagram(url) {
    var diagram = $("#distribution");
    diagram.show();
    diagram.attr("src", url);
    $("#download-form").find("input[type='hidden']").attr("value", url);
}

function updateTime(time) {
    $(".time").text("Time: " + time);
}

function updateDegreeOverTimeDiagram(url) {
    $("#degree-over-time").attr("src", url);
    $("#download-degree").find("input[type='hidden']").attr("value", url);
}

function updatePathOverTimeDiagram(url) {
    $("#path-over-time").attr("src", url);
    $("#download-path").find("input[type='hidden']").attr("value", url);
}

function deleteProjectFromPage() {
    var rowToDelete = $("#projects").find("input[value = '"
					+ window.project + "']").attr("class").split(" ")[0];
    $("." + rowToDelete).remove();
}

function showDownloadBar() {
    $("#download-bar").show();
}

function warningMessage(message, element) {
    var warningMessage = $("#" + element + "-warning");
    warningMessage.empty();
    warningMessage.append('<div class="ui-corner-all ui-state-error"> <p>'
        + '<span class="ui-icon ui-icon-alert"></span><b>Warning! </b>'
        +  message + '</p></div></div>');
}

function registrationFormVisibility() {
    var registrationForm = $("#registration");
    if (registrationForm.is(":visible")) registrationForm.hide();
    else registrationForm.show();
}

/**
 * Jump to the registration form.
 */
function scrollToRegistrationForm() {
	var MILLI_SECONDS = 2000;
	$('html, body').animate({
		scrollTop: $("#registration").offset().top
	}, MILLI_SECONDS);
}

function removeProgressBar() {
    $("#progressbar").remove();
}

function createWaitingBar(element) {
    removeProgressBar();
    element.append('<div id="progressbar">Please, wait...</div>');
     $( "#progressbar" ).progressbar({
        value: false
     });
}