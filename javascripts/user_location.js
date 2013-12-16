// input_string  are the coordinates of my apartment,
// they will be used if google.geolocation wouldn't work
// you can put here the string from your file, 
// in which you were finding the location, using ip-address
// also, should mention, there is a variable search_string_for_wiki
// it contains the name of the city, where user is
// you can use it to create requests for wikipedia
var input_string = "You : 51.0293767, 13.749075100000027"
var my_name = ''
var my_lat = ''
var my_lng = ''
var my_infowindow = new google.maps.InfoWindow();
search_string_for_wiki = '';
function initialize() {	
	if (navigator.geolocation){	
		navigator.geolocation.getCurrentPosition(function(position) {
			my_lat = position.coords.latitude;
			my_lng = position.coords.longitude;
			my_name = 'You'
			further();
		});
	} else {
		tmp_name_and_location = input_string.split(/:/)
		my_name = tmp_name_and_location[0]
		tmp_lat_and_long = tmp_name_and_location[1].split(/\,/)
		my_lat = tmp_lat_and_long[0]
		my_lng = tmp_lat_and_long[1]
		further();
	}
}
function further () {
	var my_lat_lng = new google.maps.LatLng (parseFloat (my_lat), parseFloat (my_lng))
	alert (my_lat_lng)
	var mapOptions = {
        center: my_lat_lng,
        zoom: 7
    };
	map = new google.maps.Map(document.getElementById("map-canvas"),
        mapOptions);
	var marker_me = new google.maps.Marker ({
		position: my_lat_lng,
		map: map,
		title: my_name
	});
	geocoder = new google.maps.Geocoder();
	geocoder.geocode({'latLng': my_lat_lng}, function(results, status) {
		if (status == google.maps.GeocoderStatus.OK) {
			if (results[1]) {
//it is just city name in Windows, but Ubuntu returns also POstCode - index 
				search_string_and_index = results[1].formatted_address.split(/\,/)[1];
				search_string_for_wiki = search_string_and_index.replace(/[0-9]+/, "")
				my_infowindow.setContent(search_string_for_wiki);
				my_infowindow.open(map, marker_me);
			} else {
				alert('No results found');
			}
		} else {
			alert('Geocoder failed due to: ' + status);
		}
	});
	insert_map_content();
}
google.maps.event.addDomListener(window, 'load', initialize);