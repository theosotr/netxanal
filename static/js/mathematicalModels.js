function erdosRenyiModel() {
    $("#number-nodes").slider("option", "max", 500);
    var parameters = $("#parameters");
    $("#modelDescription").text("Chooses each of the possible edges with a " +
				"given probability.");
    parameters.empty();
    parameters.append('<label for="probability">Probability of Edge Creation: </label>'
            + '<input id="probability" name="probability">'
            + '<div style="display: inline-block;" id="probability-warning" class="ui-widget"></div><br>');
    parameters.append('<label for="g-type">Graph type: </label>'
            + '<div id="g-type" style="display: inline-block;">'
            + '<input id="undirected" type="radio" name="graphtype" value="Undirected" '
            + 'checked><label for="undirected">Undirected</label><input id="directed" '
            + 'type="radio" name="graphtype" value="Directed"><label for="directed">'
            + 'Directed</label></div><br><br>');
    $("#g-type").buttonset();
    $( "#probability" ).spinner({
        spin: function( event, ui ) {
            var lowerLimit = 0;
            var upperLimit = 1.0;
            if ( ui.value > upperLimit ) {
                $( this ).spinner( "value", lowerLimit );
                return false;
            } else if ( ui.value < lowerLimit ) {
                $( this ).spinner( "value", upperLimit);
                return false;
            }
        },
        step: .001
    });
}

function wattsStrogatzModel() {
    $("#number-nodes").slider("option", "max", 500);
    var parameters = $("#parameters");
    $("#modelDescription").text("Generates a graph which has similar " +
				"characteristics with small-world netowrks");
    parameters.empty();
    parameters.append('<label for="probability">Probability of Edge Creation: </label>'
            + '<input id="probability" name="probability">'
            + '<div style="display: inline-block;" id="probability-warning" class="ui-widget"></div><br>');
    parameters.append('<label for="degree-selector">Degree: </label>'
            + '<input id="degree-selector" name="edges">'
            + '<div style="display: inline-block;" id="degree-warning" class="ui-widget"></div><br>');
    parameters.append('<label for="is-connected">Is connected: </label>'
            + '<div id="is-connected" style="display: inline-block;">'
            + '<input checked name="isConnected" value="Yes" type="radio" id="yes">'
            + '<label for="yes">Yes</label><input name="isConnected" value="No" '
            + 'type="radio" id="no-answer"><label for="no-answer">No</label</div><br><br>');
    $( "#probability" ).spinner({
        spin: function( event, ui ) {
            var lowerLimit = 0;
            var upperLimit = 1.0;
            if ( ui.value > upperLimit ) {
                $( this ).spinner( "value", lowerLimit );
                return false;
            } else if ( ui.value < lowerLimit ) {
                $( this ).spinner( "value", upperLimit);
                return false;
            }
        },
        step: .001
    });
    $("#is-connected").buttonset();
    $( "#degree-selector" ).spinner({
        spin: function( event, ui ) {
            var lowerLimit = 0;
            var upperLimit = $("#number-nodes").slider().slider("value") - 1;
            if ( ui.value > upperLimit ) {
                $( this ).spinner( "value", lowerLimit );
                return false;
            } else if ( ui.value < lowerLimit ) {
                $( this ).spinner( "value", upperLimit);
                return false;
            }
        }
    });
}

function binomialModel() {
    erdosRenyiModel();
}

function randomRegularGraph() {
    $("#number-nodes").slider("option", "max", 500);
    var parameters = $("#parameters");
    $("#modelDescription").text("Generates a graph whose nodes have " +
            "the given degree");
	parameters.empty();
    parameters.append("<label for='degree-selector'>Degree of each node: </label>" +
            "<input id='degree-selector' name='degree'>"
            + '<div style="display: inline-block;" id="degree-warning" class="ui-widget"></div>');
    $( "#degree-selector" ).spinner({
        spin: function( event, ui ) {
            var lowerLimit = 0;
            var upperLimit = $("#number-nodes").slider().slider("value") - 1;
            if ( ui.value > upperLimit ) {
                $( this ).spinner( "value", lowerLimit );
                return false;
            } else if ( ui.value < lowerLimit ) {
                $( this ).spinner( "value", upperLimit);
                return false;
            }
        }
    });
}

function randomGraph() {
    $("#number-nodes").slider("option", "max", 500);
    var parameters = $("#parameters");
    $("#modelDescription").text("Generates a graph whose nodes have " +
				"the given degree");
    parameters.empty();
    parameters.append("<label for='edges-selector'>Number of edges: </label>"
            + "<input id='edges-selector' name='edges'><br><br>");
    parameters.append('<label for="g-type">Graph type: </label>'
            + '<div id="g-type" style="display: inline-block;">'
            + '<input id="undirected" type="radio" name="graphtype" value="Undirected" '
            + 'checked><label for="undirected">Undirected</label><input id="directed" '
            + 'type="radio" name="graphtype" value="Directed"><label for="directed">'
            + 'Directed</label></div><br><br>');
    $("#edges-selector").spinner();
    $("#g-type").buttonset();
}

function barabasiAlbertModel() {
    $("#number-nodes").slider("option", "max", 50);
    var parameters = $("#parameters");
    $("#modelDescription").text("Generates a growing graph based on" +
		    "preferential attachment model.");
    parameters.empty();
    parameters.append('<label for="g-type">Graph type: </label>'
            + '<div id="g-type" style="display: inline-block;">'
            + '<input id="undirected" type="radio" name="graphtype" value="Undirected" '
            + 'checked><label for="undirected">Undirected</label><input id="directed" '
            + 'type="radio" name="graphtype" value="Directed"><label for="directed">'
            + 'Directed</label></div><br><br>');
    $("#g-type").buttonset();

}

function selectModel() {
    var graphModel = $("#model").val();
    switch (graphModel) {
        case "erdos":
            erdosRenyiModel();
            break;
        case "watts_strogatz":
            wattsStrogatzModel();
            break;
        case "binomial":
            binomialModel();
            break;
        case "regular":
            randomRegularGraph();
            break;
        case "random":
            randomGraph();
            break;
        case "barabasi":
            barabasiAlbertModel();
            break;
    }
}