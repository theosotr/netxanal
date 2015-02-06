var timeOut;
var overwriteForm;
var saveDialog;
var saveCompleted;
$(function() {
    initializeResizableComponents();
    $("#operations").accordion({
                heightStyle: "content"
            });
    $(".sortButtons").button();
    $("#findCommunities").button();
    $("#source").selectmenu({
        change: function(event) {
            event.preventDefault();
            findPaths();
        }
    });
    $("#target").selectmenu({
        change: function(event) {
            event.preventDefault();
            findPaths();
        }
    });
    $("#update-layout").selectmenu({
        change: function(event, ui) {
            event.preventDefault();
            updateImage('layout');
        }
    })
    $("#path-type").buttonset();
    $("#findPath").button();
    $("#update-node_size").slider({
        min: 50,
        max: 2100,
        value:500,
        change: function(event) {
            clearTimeout(timeOut);
            setTimeout(function() {
                updateImage("node_size")
            }, 500);
        }
    });
    $("#update-edge_width").slider({
        min: 0.1,
        max:3,
        value:1,
        change: function(event) {
            clearTimeout(timeOut);
            setTimeout(function() {
                updateImage("edge_width")
            }, 500);
        }
    });
    $("#update-font_size").slider({
        min:0,
        max:30,
        value:12,
        change: function(event) {
            clearTimeout(timeOut);
            setTimeout(function() {
                updateImage("font_size")
            }, 500);
        }
    });
    $("#pages").buttonset();
    $("#update-node_shape").buttonset();
    $("#update-node_labels").buttonset();
    $("#update-edge_labels").buttonset();
    $("#update-edge_style").selectmenu({
        change: function(event) {
            event.preventDefault();
            updateImage("edge_style")
        }
    });
    $("#level").selectmenu();
    $("#tooltip").tooltip();
    $("#actions").buttonset();
    $("#rankings").buttonset();
    $("button").button();
    $("#addition-deletion").buttonset();
    $("#tabs").tabs();
    $("#selectBar").selectmenu();
    initializeForms();
    $("#analysis").buttonset();
    $(".time-selector").slider({
        min: 1,
        max:100,
        value:50,
        change: function(event, ui) {
            updateTime(ui.value)
        }
    });
});

function initializeResizableComponents() {
    $("#node").resizable({
       maxHeight: 80,
       minHeight: 40,
       minWidth: 50,
       maxWidth: 100
    });
}

function initializeForms() {
     saveDialog = $( "#save-form" ).dialog({
        autoOpen: false,
        height: 300,
        width: 350,
        modal: true,
        buttons: {
            "Save graph": function() {
                var graphName = $("#graph-name").val();
                if (graphName == "") createWarningMessage("Field is required");
                else saveProject(graphName);

            },
            Cancel: function() {
                saveDialog.dialog( "close" );
            }
        }
     });
     overwriteForm = $( "#overwrite-form" ).dialog({
         autoOpen: false,
         resizable: false,
         height: 280,
         modal: true,
         buttons: {
             "Yes": function() {
                 var graphName = $("#graphName").text();
                 saveProject(graphName, true);
                 overwriteForm.dialog( "close" );
                 saveDialog.dialog("close");
             },
             "No": function() {
                 $( this ).dialog( "close" );
             }
     }});
    saveCompleted = $( "#save-completed" ).dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            Ok: function() {
                $( this ).dialog( "close" );
            }
        }
    });
    $( "#diagram-selector" ).dialog({
        modal: true,
        width: 500,
        buttons: {
            Ok: function() {
                if ($("#dynamic-parameters").is(":visible")) {
                    dynamicAnalysis($(".time-selector")
                        .slider().slider("value"));
                    var index = $('#tabs a[href="#dynamicDiv"]').parent().index();
                    $("#tabs").tabs("option", "active", index);
                } else
                    selectDiagram($("#measure").val());
                $("#box-info").show();
                $(this).dialog( "close" );
            }
        },
        close: function() {
            if (!$("#box-info").is(":visible")
                && !$("#dynamicDiv").find("div").is(":visible"))
                location.href = "graph";
        }
    });
    $( "#save-button" ).on( "click", function() {
        saveDialog.dialog( "open" );
    });
}