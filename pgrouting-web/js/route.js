DrawPoints = OpenLayers.Class(OpenLayers.Control.DrawFeature, {

    // this control is active by default
    autoActivate: true,

    initialize: function(layer, options) {
        // only points can be drawn
        var handler = OpenLayers.Handler.Point;
        OpenLayers.Control.DrawFeature.prototype.initialize.apply(
            this, [layer, handler, options]
        );
    },

    drawFeature: function(geometry) {
        OpenLayers.Control.DrawFeature.prototype.drawFeature.apply(this, arguments);
        if (this.layer.features.length == 1) {
            var style = OpenLayers.Util.applyDefaults(style, OpenLayers.Feature.Vector.style['default']);
            style.fillOpacity = 1;
            style.strokeWidth = 1;
            style.fillColor = "#ff0000";
            this.layer.features[0].style = style;
            this.layer.redraw();
        } else if (this.layer.features.length == 2) {
            var style = OpenLayers.Util.applyDefaults(style, OpenLayers.Feature.Vector.style['default']);
            style.fillOpacity = 1;
            style.strokeWidth = 1;
            style.fillColor = "#00ff00";
            this.layer.features[1].style = style;
            this.layer.redraw();

            this.deactivate();            
        }
    }
});


var map, osm_layer, vector_layer, point_layer;
var epsg_4326, epsg_900913;
var proj_opts;
var route_method;
        
function init(){
    epsg_4326 = new OpenLayers.Projection("EPSG:4326");
    epsg_900913 = new OpenLayers.Projection("EPSG:900913");
    proj_opts = {
        'internalProjection': epsg_900913,
        'externalProjection': epsg_4326
    };
    route_method = "SPD";

    map = new OpenLayers.Map('map');

    osm_layer = new OpenLayers.Layer.OSM("OpenLayers OSM");
    vector_layer = new OpenLayers.Layer.Vector("routelayer", {
        styleMap: new OpenLayers.StyleMap(new OpenLayers.Style({
            strokeColor: "#000000",
            strokeWidth: 3
        }))
    });
    point_layer = new OpenLayers.Layer.Vector("pointlayer");

    map.addLayers([osm_layer, vector_layer, point_layer]);

    var draw_points = new DrawPoints(point_layer);
    var drag_points = new OpenLayers.Control.DragFeature(point_layer, {
        autoActivate: true
    });
    map.addControls([draw_points, drag_points]);

    drag_points.onComplete = function() {
        pgrouting();
    };

    point_layer.events.on({
            featureadded: function() {
            pgrouting();
        }
    });

    map.setCenter(new OpenLayers.LonLat(12953390, 4848000), 11);
}

function pgrouting() {
    if (point_layer.features.length == 2) {
        vector_layer.removeAllFeatures();

        var startpoint = point_layer.features[0].geometry.clone();
        startpoint.transform(epsg_900913, epsg_4326);

        var finalpoint = point_layer.features[1].geometry.clone();
        finalpoint.transform(epsg_900913, epsg_4326);

        $.ajax({
            url: "../php/pgrouting.php",
            data: {
                startpoint: startpoint.x + " " + startpoint.y,
                finalpoint: finalpoint.x + " " + finalpoint.y,
                method: route_method
            },
            success: plot_route
        });
    }
}

function plot_route(jsondata) {
    var decoder = new OpenLayers.Format.GeoJSON(proj_opts);
    var features = decoder.read(jsondata);
    if (features) {
        if (features.constructor != Array) {
            features = [features];
        }
        vector_layer.addFeatures(features);
    }
}
