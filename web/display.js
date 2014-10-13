var map;

function initialize() {
    map = new GMap();
}


var Shape = function(shape_id,shape_layer) {
    this.shape_id = shape_id;
    this.layer = shape_layer;
    this._orig_layer = null;
}

var Stop = function(stop_id,stop_layer) {
    this.stop_id = stop_id;
    this.layer = stop_layer;
    this._orig_layer = null;
}

var Map = function () {
    
}

Map.prototype.drawShape = function (shape_id,points) {
    
};

Map.prototype.drawStop = function (stop_id,stop_coord) {
    
};

Map.prototype.clear = function () {
    
};

Map.prototype.getShapeStr = function () {
    
};

Map.prototype.getStopStr = function () {
    
};

Map.prototype.edit = function (bool) {
    
};

Map.prototype.cancelEdit = function () {

};

Map.prototype.saveEdits = function () {
    
};

Map.prototype.zoomAll = function () {
    
};

Map.prototype.zoomShapes = function (shape_id) {
    
};

Map.prototype.zoomStops = function (stop_id) {
    
};

var GMap = function() {
    var cent = new google.maps.LatLng(37.9061,-122.5450);
    var opts = {
    zoom: 9,
    center: cent,
    mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    this.map_object = new google.maps.Map(document.getElementById("map-canvas"), opts);
    this.shapes = [];
    this.stops = [];
    
    this.edit_shape = null;
    this.edit_stop = null;

    // allow editing and cancel editing higher than this #
    this.zoom_cutoff = 15;
}

GMap.prototype = new Map();
GMap.prototype.constructor = GMap;

GMap.prototype.drawShape = function (shape_id,points,color) {
    gpoints = []
    for (var i=0; i< points.length; i++) {
        gpoints.push(new google.maps.LatLng(points[i][0],points[i][1]));
    }
    
    var gcolor;

    if (color != null) {
        gcolor = '#' + color;
    }
    else {
        gcolor = '#AA0000';
    }

    var directionSymbol = {path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW};
    
    var pline = new google.maps.Polyline({
                                         path: gpoints,
                                         strokeColor: gcolor,
                                         strokeOpacity: 1.0,
                                         strokeWeight: 3,
                                         clickable: true,
                                         editable: false,
                                         icons: [{
                                                 icon: directionSymbol,
                                                 offset: '100%'
                                                 }]
                                         });
    pline.setMap(this.map_object);
    var shape = new Shape(shape_id,pline);
    var orig_line = new google.maps.Polyline({path: gpoints});
    shape._orig_layer = orig_line;
    this.edit_shape = shape;
    this.shapes.push(shape);
};

GMap.prototype.drawStop = function (stop_id,stop_coord) {
    pos = new google.maps.LatLng(stop_coord[0],stop_coord[1]);
    var stop_marker = new google.maps.Marker({position:pos,map:this.map_object});
    var orig_marker = new google.maps.Marker({position:pos});
    var stop = new Stop(stop_id,stop_marker);
    stop._orig_layer = orig_marker;
    this.edit_stop = stop;
    this.stops.push(stop);
};

GMap.prototype.clearAll = function () {
    this.clearStops();
    this.clearShapes();
};

GMap.prototype.clearStops = function () {
    while(this.stops.length > 0) {
        stop = this.stops.pop()
        stop.layer.setMap(null);
        stop = null;
    }
};

GMap.prototype.clearShapes = function() {
    while(this.shapes.length > 0) {
        shape = this.shapes.pop()
        shape.layer.setMap(null);
        shape = null;
    }
};

GMap.prototype.edit = function (bool) {
    if (this.edit_shape != null) {
        this.edit_shape.layer.setEditable(bool);
    }
    if (this.edit_stop != null) {
        this.edit_stop.layer.setDraggable(bool);
    }
  
};


GMap.prototype.cancelEditLayers = function() {
    this.edit(false);
};

GMap.prototype.cancelEdit = function () {
    if (this.map_object.getZoom() > this.zoom_cutoff) {
        this.cancelEditLayers();
        if (this.edit_stop != null) {
            this.edit_stop.layer.setPosition(this.edit_stop._orig_layer.getPosition());
        }
        if (this.edit_shape != null) {
            this.edit_shape.layer.setPath(this.edit_shape._orig_layer.getPath());
        }
    }
};

// is there a json possibility?
GMap.prototype.saveEdits = function () {
    this.cancelEditLayers();
    dshape.set_text(this.getShapeStr());
    dstop.set_text(this.getStopStr());
};

GMap.prototype.getShapeStr = function () {
    if (this.edit_shape == null) {
        return '';
    }
    else {
        return this.edit_shape.shape_id + '=' + this.edit_shape.layer.getPath().getArray().join();
    }
};

GMap.prototype.getStopStr = function () {
    if (this.edit_stop == null) {
        return '';   
    }
    else { 
        return this.edit_stop.stop_id + '=' + this.edit_stop.layer.getPosition().toString();
    }
};

GMap.prototype.zoomAll = function () {

    var bounds = new google.maps.LatLngBounds();
    for (var i in this.shapes) {
        var coord_array = this.shapes[i].layer.getPath().getArray();
        for (j in coord_array) {
            bounds.extend(coord_array[j]);
        }
    }
    for (var i in this.stops) {
        bounds.extend(this.stops[i].layer.getPosition());
    }
    this.map_object.fitBounds(bounds);
};

GMap.prototype.zoomShape = function (shape_id) {

    var bounds = new google.maps.LatLngBounds();
    for (var i in this.shapes) {
        if (this.shapes[i].shape_id == shape_id) {
            var coord_array = this.shapes[i].layer.getPath().getArray();
            for (j in coord_array) {
                bounds.extend(coord_array[j]);
            }
            break;
        }
    }
    this.map_object.fitBounds(bounds);
};

GMap.prototype.zoomStop = function (stop_id) {
    var bounds = new google.maps.LatLngBounds();
    for (var i in this.stops) {
        if (this.stops[i].stop_id == stop_id){
            bounds.extend(this.stops[i].layer.getPosition());
            break;
        }
    }
    this.map_object.fitBounds(bounds);
};

google.maps.event.addDomListener(window, 'load', initialize);
