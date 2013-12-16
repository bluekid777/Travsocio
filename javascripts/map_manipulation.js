//just assign another value for the input string (from your file, it should work)
function initialize () {
var input_string = "You: 51.0293767, 13.749075100000027; Neighbour1 : 51.37, 13.85; Neighbour2: 50.92, 13.33"
var location_name_array = []
var location_lat_array = []
var location_lng_array = []
location_array = input_string.split(/;/)
	for (i = 0; i < location_array.length; i++) {
		tmp_name_and_location = location_array[i].split(/:/)
		location_name_array[i] = tmp_name_and_location[0]
		tmp_lat_and_long = tmp_name_and_location[1].split(/\,/)
		location_lat_array [i] = tmp_lat_and_long[0]
		location_lng_array [i] = tmp_lat_and_long[1]
		}
	var my_lat_lng = new google.maps.LatLng (parseFloat (location_lat_array [0]), parseFloat (location_lng_array [0]))
	var mapOptions = {
        center: my_lat_lng,
        zoom: 7
    };
	map = new google.maps.Map(document.getElementById("map-canvas"),
        mapOptions)	
	for (i = 0; i < location_array.length; i++)	{

		var place_lat_lng = new google.maps.LatLng (parseFloat(location_lat_array[i]), parseFloat(location_lng_array[i]))
		var marker = new google.maps.Marker ({
			position: place_lat_lng,
			map: map,
			title: location_name_array[i]
		});
		var infowindow = new google.maps.InfoWindow();
		infowindow.setContent(location_name_array[i]);
		infowindow.open(map, marker);				
	}
}
google.maps.event.addDomListener(window, 'load', initialize);