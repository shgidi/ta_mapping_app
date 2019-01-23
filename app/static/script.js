// https://www.w3schools.com/tags/tryit.asp?filename=tryhtml_form_submit
// https://www.w3schools.com/js/tryit.asp?filename=tryjs_validation_js

// window.onload = function() {
// 	// setup the button click
// 	document.getElementById("down").onclick = function() {
// 		doWork("down")
// 		console.log('down')
// 	};
// 	document.getElementById("up").onclick = function() {
// 		doWork("up")
		
// 	};
// }



function doWork(dir) {
	// ajax the JSON to the serverreceiverreceiver
	$.post("receiver", {"dir": dir}, function(){
		document.getElementById('map').contentWindow.location.reload();
		console.log('a')
	});
	// stop link reloading the page
 event.preventDefault();
}


function addressSearch() {
  var address = document.forms["myForm"]["address"].value;
  var time = document.forms["myForm"]["time"].value;
  //location.reload(); //reload page
  $.post("address_search", {"address":address,'time':time}, function(err, req, resp){
  	//document.getElementById('map').contentWindow.location.reload();
  	
  	$("#demo").html(resp["responseJSON"]['route']);
  	//$("#map").contents().find("body").replaceWith('');
  	$("#map").contents().find("body").html(resp["responseJSON"]['map']);
   });
  return false;
}