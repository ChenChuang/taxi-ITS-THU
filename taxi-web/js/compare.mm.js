var ranks = {};
var alg = 'bn';
var json_buffer = {};

var map, osm_layer, vector_layer, point_layer;
var epsg_4326, epsg_900913;
var proj_opts;
var features_data;
var features = [];
var selected_f;
var url;
var s_style, t_style, m_style;
var selectctrl, selectpointctrl;
var tid;
var tids;
var tid_i = -1;
var track_filename;
var path_filename;
      
function init() {
    init_star();
    init_ranks();
    init_map();
    document.onkeypress = on_key_press;
}

function init_ranks() {
    ranks = {'bn':0, 'st':0, 'iv':0, 'ut':0, 'uti':0};
    alg = 'bn';
}

function init_map() {
	epsg_4326 = new OpenLayers.Projection("EPSG:4326");
	epsg_900913 = new OpenLayers.Projection("EPSG:900913");
	proj_opts = {
		'internalProjection': epsg_900913,
		'externalProjection': epsg_4326
	};

	map = new OpenLayers.Map('map');

	osm_layer = new OpenLayers.Layer.OSM("OpenLayers OSM");
	var defaultstyle = new OpenLayers.Style({
        strokeColor:"#000000", 
        strokeWidth:2, strokeOpacity:1});
	var tempstyle = new OpenLayers.Style({
        strokeColor:"#ff0000", 
        strokeWidth:3, strokOpacity:1.0});
	var selectstyle = new OpenLayers.Style({
        strokeColor:"#0000ff", 
        strokeWidth:3, strokOpacity:1.0});
	vector_layer = new OpenLayers.Layer.Vector("routelayer", {styleMap: new OpenLayers.StyleMap({
        'default':defaultstyle, 
        'temporary':tempstyle, 
        'select':selectstyle})});
	point_layer = new OpenLayers.Layer.Vector("pointlayer");
	
	map.addLayers([osm_layer, vector_layer, point_layer]);


	var highlightctrl = new OpenLayers.Control.SelectFeature(vector_layer, {
        hover:true, 
        highlightOnly:true, 
        renderIntent:"temporary"});
	map.addControl(highlightctrl);
	highlightctrl.activate();

	map.addControl(new OpenLayers.Control.MousePosition({displayProjection:epsg_4326}));

	map.setCenter(new OpenLayers.LonLat(12953390, 4848000), 11);

	t_style = {
                strokeColor: "#00FF00",
				strokOpacity: 1,
				fillColor: "#00ff00",
				fillOpacity: 0.5,
                pointRadius: 5,
            };

	s_style = {
                strokeColor: "#FF0000",
				strokOpacity: 1,
				fillColor: "#FF0000",
				fillOpacity: 0.5,
                pointRadius: 5,
            };
	m_style = {
                strokeColor: "#0000ff",
				strokOpacity: 1,
				fillColor: "#0000ff",
				fillOpacity: 0.3,
                pointRadius: 5,
            };
}

function init_star() {
    $('#star').raty();
    $('#star').raty({
        score : 0,
        path : '../img',
        click: function(score, e) {
            set_alg_rank(score);
            set_alg_button(alg, ranks[alg])
        }
    });
}

function init_alg_buttons() {
    for(alg in ranks) {
        set_alg_button(alg, 0)
    }
}

function on_key_press(e) {
    e = (e) ? e : window.event;
    if (49 <= e.charCode <= 53 && document.activeElement.id != "fromtid_tx" && document.activeElement.id != "totid_tx") {
        set_alg_rank(e.charCode - 48);
        set_alg_button(alg, ranks[alg])
        $('#star').raty('score', get_alg_rank()); 
    }
}


function set_star(rank) {
    $('#star').raty({ score: rank });
}

function set_alg_rank(rank) {
    ranks[alg] = rank;
}

function get_alg_rank() {
    return ranks[alg];
}

function set_alg(str) {
    alg = str;
}

function get_alg() {
    return alg;
}

function get_tids_compare(fromtid, totid) {
	if(totid < 0) {
        if(fromtid >= 0) {
            tids = Array()
            tids[0] = {'tid':fromtid};
            tid_i = -1;
            next();
            set_tid_info('TID: ' + fromtid);
        }
    }else{
        url = "../php/get_tids_compare.php";
	    tid_i = -1;
	    $.ajax({
		    url: url,
		    data: {fromtid:fromtid, totid:totid},
  		    success: get_tids_done,
		    error: info_error
	    });
    }
}

function get_tids_done(data) {
	if (data == ':(') {
		set_tid_info(':(');
	}else {
		tids = $.parseJSON(data);
		if (tids.length > 0) {
			set_tid_info(tids.length + ' Left. COME ON !!');
		} else {
			set_tid_info('All DONE :D');
		}
	}
}

function next() {
	tid_i = tid_i + 1;
    if(tid_i >= tids.length) {
		set_tid_info('All DONE :D');
	}else {
        set_tid_info(tids[tid_i]['tid']); 
    }
	vector_layer.removeAllFeatures();
	point_layer.removeAllFeatures();
    init_ranks()
    init_star()
    init_alg_buttons()
	set_alg_info(':|');	
}

function upload_ranks() {
	url = "../php/upload_ranks.php";
    for (var k in ranks) {
        ranks[k] = Math.max(1, ranks[k]);
        ranks[k] = Math.min(5, ranks[k]);
    }
	$.ajax({
		url: url,
		data: $.extend({tid:tid}, ranks),
  		success: set_alg_info,
		error: info_error
	});
}

function get_data() {
	set_alg_info(':|');	
	tid = tids[tid_i]['tid'];
	set_tid_info(tid);
	track_filename = "geojson_t_" + tid;
	get_track_data();
}

function get_track_data() {
    var filename = track_filename;
    if (json_buffer[filename] != undefined) {
        get_track_done(json_buffer[filename]);
    }
	if (filename) {
		url = "../data/tracks/" + filename;
		if(!url.match(/json$/)){
			str = url + ".json";		
		}
		$.ajax({
			url: url,
  			success: get_track_done,
			error: info_error
		});
	}
}

function get_track_done(jsondata) {
	//plot_track(jsondata, false);
    var filename = track_filename;
    if (json_buffer[filename] == undefined) {
        json_buffer[filename] = jsondata;
    }
	plot_gps(jsondata);
	path_filename = "geojson_p_" + alg + "_" + tid;
	get_path_data(path_filename);
}

function get_path_data(filename) {
    var filename = path_filename;
    if (json_buffer[filename] != undefined) {
        get_path_done(json_buffer[filename])
    }
	if (filename) {
		url = "../data/paths/" + filename;
		if(!url.match(/json$/)){
			str = url + ".json";		
		}
		$.ajax({
			url: url,
  			success: get_path_done,
			error: info_error
		});
	}
}

function get_path_done(jsondata) {
    var filename = path_filename;
	if (json_buffer[filename] == undefined) {
        json_buffer[filename] = jsondata;
    }
    plot_track(jsondata);
}

function plot_track(jsondata) {	
	features = [];
	vector_layer.removeAllFeatures();
	var geojsoner = new OpenLayers.Format.GeoJSON(proj_opts);
	var tmp_fs = geojsoner.read(jsondata);
	if(tmp_fs) {
		if(tmp_fs.constructor != Array) {
			tmp_fs = [tmp_fs];
		}
		features = features.concat(tmp_fs);
        vector_layer.addFeatures(features);		
	}else{
		alert(url + " is broken");
	}
}

function replot_track() {
	vector_layer.removeAllFeatures();
	point_layer.removeAllFeatures();
	selectctrl.activate();
	vector_layer.addFeatures(features);
	selectctrl.unselect(selected_f);
}

function plot_gps(jsondata) {
	point_layer.removeAllFeatures();
	var geojsoner = new OpenLayers.Format.GeoJSON(proj_opts);
	var feature = geojsoner.read(jsondata);
	if(feature) {
		if(feature.constructor == Array) {
			feature = feature[0];
		}
		var lonlats = feature.geometry.clone().transform(epsg_900913, epsg_4326).getVertices();
		var lonlats2 = feature.geometry.getVertices();

		var pnum = lonlats2.length;
		var points = [];

		for(var i=1; i < pnum-1; i++){
			points.push(new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(lonlats2[i].x, lonlats2[i].y), null, m_style));	
		}
		points.push(new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(lonlats2[0].x, lonlats2[0].y), null, s_style));	
		points.push(new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(lonlats2[pnum-1].x, lonlats2[pnum-1].y), null, t_style));	
		point_layer.addFeatures(points);
	}else{
		alert(url + " is broken");
	}
}

function clear() {
}

function info_error(e) {
	alert(e);
}

