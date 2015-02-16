var timeOut;
var overwriteForm;
var saveDialog;
var saveCompleted;
var deletion;
$(function() {
    initializeResizableComponents();
    initializeAccordion();
    initializeTabs();
    initializeButtons();
    initializeButtonSets();
    initializeForms();
    initializeToolTip();
    initializeSelectMenus();
    initializeSliders();
    initializeSpinners();
});
function initializeSelectMenus() {
    $("#source").selectmenu();
    $("#target").selectmenu();
    $("#model").selectmenu({
        change: function(event) {
            event.preventDefault();
            selectModel();
        }
    });
    $("#update-layout").selectmenu({
        change: function(event) {
            event.preventDefault();
            updateImage('layout');
        }
    });
    $("#update-edge_style").selectmenu({
        change: function(event) {
            event.preventDefault();
            updateImage("edge_style")
        }
    });
    $("#level").selectmenu();
    $("#selectBar").selectmenu();
}

function initializeButtonSets() {
    $("#pages").buttonset();
    $("#update-node_shape").buttonset();
    $("#update-node_labels").buttonset();
    $("#update-edge_labels").buttonset();
    $("#path-type").buttonset();
    $("#addition-deletion").buttonset();
    $("#rankings").buttonset();
    $("#g-type").buttonset();
    $("#graph-type").buttonset();
    $("#projects").buttonset();
    $("#calculationWay").buttonset();
    $("#analysis").buttonset();
}

function initializeButtons() {
    $("button").button();
}

function initializeToolTip() {
    $("#tooltip").tooltip();
}

function initializeTabs() {
    $("#tabs").tabs();
    $("#graph-creation").tabs();
}

function initializeAccordion() {
    $("#operations").accordion({
        heightStyle: "content"
    });
}
function initializeSliders() {
   $(".time-selector").slider({
        min: 1,
        max:100,
        value:50,
        change: function(event, ui) {
            updateTime(ui.value)
        }
    });
    $("#update-font_size").slider({
        min:0,
        max:30,
        value:12,
        change: function() {
            clearTimeout(timeOut);
            setTimeout(function() {
                updateImage("font_size")
            }, 500);
        }
    });
    $("#update-node_size").slider({
        min: 50,
        max: 2100,
        value:500,
        change: function() {
            clearTimeout(timeOut);
            setTimeout(function() {
                updateImage("node_size")
            }, 500);
        }
    });
    $("#update-edge_width").slider({
        min: 0,
        max:3,
        value:1,
        change: function() {
            clearTimeout(timeOut);
            setTimeout(function() {
                updateImage("edge_width")
            }, 500);
        },
        step: .01
    });
    $("#number-nodes").slider({
        min: 2,
        max:500,
        value:50,
        change: function() {
            $("input[name='nodes']").attr("value", $(this).slider().slider("value"));
            $("#nodes").text($(this).slider().slider("value"));
        }
    });
}

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
    deletion = $( "#before-deletion" ).dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            Yes: function() {
                deleteProject();
                $(this).dialog("close");
            },
            No: function() {
                $(this).dialog("close");
            }

        }
    });
    $( "#diagram-selector" ).dialog({
        modal: true,
        width: 500,
        buttons: {
            Ok: function() {
                var tabs = $("#tabs");
                if ($("#dynamic-parameters").is(":visible")) {
                    dynamicAnalysis();
                    var index = tabs.find('a[href="#dynamicDiv"]').parent().index();
                    tabs.tabs("option", "active", index);
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

/**
 * Initializes jQuery Ui spinners of page.
 */
function initializeSpinners() {
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