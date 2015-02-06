
$(function() {

 
$('#btn').click(function() {
$.getJSON($SCRIPT_ROOT + '/_change_graph', {
selection: $('#layout').val(),
graphtype: $('#graph_type').text(),
size: $('input[name="size"]').val(),
edge: $('input[name="edge"]').val(),
fsize: $('input[name="fsize"]').val(),
ncolor: $('#nodecolor').val(),
ecolor: $('#edgecolor').val(),
fcolor: $('#fontcolor').val(),
estyle: $('#edgestyle').val(),
shape: $('#nodeshape').val(),
weights: $('#weights').val()
}, function(data) {
	$('#colorbase').hide();
   $('#graphImage').attr('src', data);
});
return false;
});

});



