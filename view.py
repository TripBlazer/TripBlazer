from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *

from utils import *
import json
import resources
import model

#
#
#
class DataShape(QObject):
    def __init__(self, parent=None):
        super(DataShape, self).__init__(parent)
        self.text = ''

    @pyqtSlot(str)
    def set_text(self, message):
        self.text = message
        #print message

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow,self).__init__()
        self.treeview = RouteTreeView()
        self.gtfs = None

    def layout_menu(self):
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('&File')
        self.view_menu = self.menu.addMenu('&View')
        self.help_menu = self.menu.addMenu('&Help')

        loadGtfs = QAction('&Load',self)
        loadGtfs.triggered.connect(self.load_gtfs)
        self.file_menu.addAction(loadGtfs)
    
        exportGtfs = QAction('&Export',self)
        exportGtfs.triggered.connect(self.export_gtfs)
        self.file_menu.addAction(exportGtfs)

        routeView = QAction('&Route View',self)
        routeView.triggered.connect(self.route_view)
        self.view_menu.addAction(routeView)
    
        blockView = QAction('&Block View',self)
        blockView.triggered.connect(self.block_view)
        self.view_menu.addAction(blockView)


    def layout_toolbar(self):
        tool_layout = QHBoxLayout()
        
        self.edit_button = QToolButton()
        self.edit_button.setText('Edit')
        #self.edit_button.setStyleSheet("background-color:#009900;")
        self.cancel_button = QToolButton()
        self.cancel_button.setText('Cancel')
        #self.cancel_button.setStyleSheet("background-color:#FF3300;")
        self.map_save_button = QToolButton()
        self.map_save_button.setText('Save')
        #self.map_save_button.setStyleSheet("background-color:#3366FF;")
        
        tool_layout.addWidget(self.edit_button)
        tool_layout.addWidget(self.cancel_button)
        tool_layout.addWidget(self.map_save_button)
        
        tool_layout.setAlignment(Qt.AlignLeft)

        return tool_layout


    def layout(self):

        self.layout_menu()
        self.treeview.layout()

        self.widget = QWidget(self)

        self.all_layout = QHBoxLayout()
        self.right_side = QVBoxLayout()
        self.map_layout = QVBoxLayout()
        
        tool_layout = self.layout_toolbar()


        self.map_layout = QVBoxLayout()
        self.map_layout.addWidget(self.treeview.mapview)
        
        self.right_side.addLayout(self.map_layout)
        self.right_side.addLayout(tool_layout)
        self.right_side.addLayout(self.treeview.entity_top_widget)
    
        self.all_layout.addLayout(self.treeview.top_widget,6)
        self.all_layout.addLayout(self.right_side,9)
    
        self.widget.setLayout(self.all_layout)
        self.setCentralWidget(self.widget)
        self.resize(900,600)
        self.show()

    def load_gtfs(self):
        gtfs_file = QFileDialog.getOpenFileName(self,'Open GTFS','/home')
        
        if not gtfs_file:
            return
        self.gtfs = model.GTFSModel()
        self.gtfs.load(gtfs_file)

        # we need a clear method here

        self.treeview.set_gtfs(self.gtfs)

        self.treeview.populate()

        self.edit_button.clicked.connect(self.edit)
        self.cancel_button.clicked.connect(self.cancel_edit)
        self.map_save_button.clicked.connect(self.save_edit)

    def export_gtfs(self):
        if self.gtfs:
            gtfs_file = QFileDialog.getSaveFileName(self,'Export GTFS','/home')
            self.gtfs.export(str(gtfs_file))

    def route_view(self):
        pass

    def block_view(self):
        pass

    def edit(self):
        self.treeview.edit()

    def cancel_edit(self):
        self.treeview.cancel_edit()

    def save_edit(self):
        self.treeview.save_edit()


class MapView(QWebView):

    def __init__(self, parent=None):
        super(MapView, self).__init__(parent)
        self.frame = self.page().mainFrame()
        self.top_widget = self
        self.gtfs = None
        self.dshape = DataShape()
        self.dstop = DataShape()
        #self.dmsg = DataShape()

        self.frame.addToJavaScriptWindowObject("dstop", self.dstop)
        self.frame.addToJavaScriptWindowObject("dshape", self.dshape)
        #self.frame.addToJavaScriptWindowObject("dmsg", self.dmsg)
        
    def layout(self):
        html = open('web/index.html').read()
        self.setHtml(html,QUrl('qrc:/'))

    def set_gtfs(self,gtfs):
        self.gtfs = gtfs

    def clear(self):
        """ Remove stops and shapes from map
        """
        self.frame.evaluateJavaScript('map.clearAll();')

    def clear_stops(self):
        """ Remove stops only from map
        """
        self.frame.evaluateJavaScript('map.clearStops();')

    def clear_shapes(self):
        """ Remove shapes only from map
        """
        self.frame.evaluateJavaScript('map.clearShapes();')
    
    def zoom_all(self):
        self.frame.evaluateJavaScript('map.zoomAll();')

    def zoom_stop(self,stop_id):
        self.frame.evaluateJavaScript('map.zoomStop(%s);'%stop_id)

    def zoom_shape(self,shape_id):
        self.frame.evaluateJavaScript('map.zoomAll();')
        #self.frame.evaluateJavaScript('map.zoomShape(%s);'%shape_id)

    def display_shape(self,shape,color):
        self.frame.evaluateJavaScript('map.drawShape("%s",%s,"%s");' % (shape.shape_id,json.dumps(shape.points),color))
    
    def display_stop(self,stop):
        self.frame.evaluateJavaScript('map.drawStop("%s",%s);' % (stop.stop_id,json.dumps([stop.stop_lat,stop.stop_lon])))

    def edit(self):
        self.frame.evaluateJavaScript('map.edit(true);')
    
    def cancel_edit(self):
        self.frame.evaluateJavaScript('map.cancelEdit();')

    def shape_save(self,shape_str):
        if not shape_str:
            #print 'no shape data'
            return
        try:
            shape = shape_str.split('=')
            shape_points = list(eval(str(shape[1])))
            self.gtfs.modify_shape_points(shape[0], shape_points)
        except:
            warning('problem saving shape coords')
            return

    def stop_save(self,stop_str):
        if not stop_str:
            return
        stop_id,stop_point = stop_str.split('=')
        try:
            stop_point = tuple(eval(str(stop_point)))
            self.gtfs.modify_stop_point(str(stop_id),stop_point)
        except:
            warning('problem saving stop coords')
            return


    def map_save(self):
        """ Get stop and shape data from map and save to
        GTFS.
        """
        self.frame.evaluateJavaScript('map.saveEdits();')
        #self.frame.evaluateJavaScript("dshape.set_text(map.getShapeStr());")
        #self.frame.evaluateJavaScript("dstop.set_text(map.getStopStr());")

        if self.dshape.text != '':
            self.shape_save(self.dshape.text)
        
        if self.dstop.text != '':
            self.stop_save(self.dstop.text)
        


class EntityView(object):
    """ This is an abstract class that provides methods for creating, displaying,
    and managing editable fields for GTFS data entities (route,trip,stop,etc.).
    """

    def __init__(self):
        self.top_widget = None
        self._gtfs = None
        self._view = None

        self._all_widgets = []
        # maps the entity attribute name to the editable widget
        self._editable_widgets = {}

        self._edit_entity = None

    def set_gtfs(self,gtfs):
        self.gtfs = gtfs

    def edit_widget(self,label,widget):

        self._all_widgets.append(label)
        self._all_widgets.append(widget)

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(widget)
        return layout

    def edit_line(self,descriptor):
        label = QLabel(descriptor)
        self._editable_widgets[descriptor] = QLineEdit()
        self._editable_widgets[descriptor].setReadOnly(True)

        return self.edit_widget(label,self._editable_widgets[descriptor])

    def edit_combo(self,descriptor):
        label = QLabel(descriptor)
        self._editable_widgets[descriptor] = QComboBox()
        
        return self.edit_widget(label,self._editable_widgets[descriptor])

    def edit_color(self,descriptor):
        label = QLabel(descriptor)
        self._editable_widgets[descriptor] = QColorDialog()
        
        return self.edit_widget(label,self._editable_widgets[descriptor])

    def edit_time(self,descriptor):
        label = QLabel(descriptor)
        self._editable_widgets[descriptor] = QTimeEdit()
        
        return self.edit_widget(label,self._editable_widgets[descriptor])

    def layout(self):
        raise NotImplementedError('layout not implemented')

    def hide(self):
        for widget in self._all_widgets:
            widget.hide()

    def show(self):
        for widget in self._all_widgets:
            widget.show()

    def populate(self,entity):
        raise NotImplementedError('populate not implemented')

    def add_data(self,entity):
        raise NotImplementedError('add_data not implemented')

    def clear(self):
        for edit_widget in self._editable_widgets.values():
            edit_widget.clear()

    def edit(self):
        raise NotImplementedError('edit not implemented')

    def cancel_edit(self):
        self.clear()
        if self._edit_entity:
            self.add_data(self._edit_entity)

    def save_edit(self):
        raise NotImplementedError('save_edit not implemented')

class RouteEntityView(EntityView):

    def __init__(self):
        super(RouteEntityView,self).__init__()
        self.route_types = [str(i) for i in range(8)]

    def layout(self):
        
        self.top_widget.addLayout(self.edit_line('route_short_name'))
        self.top_widget.addLayout(self.edit_line('route_long_name'))
        self.top_widget.addLayout(self.edit_line('route_desc'))

        box = QHBoxLayout()
        box.addLayout(self.edit_combo('route_type'))
        self._editable_widgets['route_type'].addItems(self.route_types)
        #box.addLayout(self.edit_color('route_color'))

        self.top_widget.addLayout(box)

    def populate(self,route):
        self.clear()
        self.add_data(route)
        self._edit_entity = route

    def add_data(self,route):
        self._editable_widgets['route_short_name'].insert(route.route_short_name)
        self._editable_widgets['route_long_name'].insert(route.route_long_name)
        self._editable_widgets['route_desc'].insert(route.route_desc)
        self._editable_widgets['route_type'].addItems(self.route_types)
        self._editable_widgets['route_type'].setCurrentIndex(int(route.route_type))
        
        self._editable_widgets['route_type'].setEnabled(False)
        self._editable_widgets['route_short_name'].setReadOnly(True)
        self._editable_widgets['route_long_name'].setReadOnly(True)
        self._editable_widgets['route_desc'].setReadOnly(True)

    def edit(self):
        self._editable_widgets['route_type'].setEnabled(True)
        self._editable_widgets['route_short_name'].setReadOnly(False)
        self._editable_widgets['route_long_name'].setReadOnly(False)
        self._editable_widgets['route_desc'].setReadOnly(False)

    def save_edit(self):
        self._edit_entity.route_type = int(self._editable_widgets['route_type'].currentText())
        self._edit_entity.route_short_name = self._editable_widgets['route_short_name'].text()
        self._edit_entity.route_long_name = self._editable_widgets['route_long_name'].text()
        self._edit_entity.route_desc = self._editable_widgets['route_desc'].text()


class TripEntityView(EntityView):

    def layout(self):
        box1 = QHBoxLayout()
        box2 = QHBoxLayout()
        box3 = QHBoxLayout()
        
        box1.addLayout(self.edit_combo('service_id'))
        box1.addLayout(self.edit_combo('shape_id'))
        box2.addLayout(self.edit_combo('route_id'))
        box2.addLayout(self.edit_combo('block_id'))
        box3.addLayout(self.edit_line('trip_headsign'))
        box3.addLayout(self.edit_combo('direction_id'))

        self._editable_widgets['direction_id'].addItems(['0','1'])

        self.top_widget.addLayout(box1)
        self.top_widget.addLayout(box2)
        self.top_widget.addLayout(box3)

    def populate(self,trip):

        self.clear()
        self.add_data(trip)
        self._edit_entity = trip

    def add_data(self,trip):

        route_ids = self.gtfs.get_route_ids()
        self._editable_widgets['route_id'].addItems(route_ids)
        self._editable_widgets['route_id'].setCurrentIndex(route_ids.index(trip.route_id))

        service_ids = self.gtfs.get_service_ids()
        self._editable_widgets['service_id'].addItems(service_ids)
        self._editable_widgets['service_id'].setCurrentIndex(service_ids.index(trip.service_id))

        shape_ids = self.gtfs.get_shape_ids()
        self._editable_widgets['shape_id'].addItems(shape_ids)
        self._editable_widgets['shape_id'].setCurrentIndex(shape_ids.index(trip.shape_id))

        block_ids = self.gtfs.get_block_ids()
        self._editable_widgets['block_id'].addItems(block_ids)
        self._editable_widgets['block_id'].setCurrentIndex(block_ids.index(trip.block_id))
        
        self._editable_widgets['direction_id'].addItems(['0','1'])
        if trip.direction_id != '0' and trip.direction_id != '1':
            self._editable_widgets['direction_id'].addItems(str(trip.direction_id))
        self._editable_widgets['direction_id'].setCurrentIndex(int(trip.direction_id))
        self._editable_widgets['trip_headsign'].insert(trip.trip_headsign)

        self._editable_widgets['trip_headsign'].setReadOnly(True)
        self._editable_widgets['service_id'].setEnabled(False)
        self._editable_widgets['shape_id'].setEnabled(False)
        self._editable_widgets['block_id'].setEnabled(False)
        self._editable_widgets['route_id'].setEnabled(False)
        self._editable_widgets['direction_id'].setEnabled(False)


    def edit(self):
        self._editable_widgets['trip_headsign'].setReadOnly(False)
        self._editable_widgets['service_id'].setEnabled(True)
        #self._editable_widgets['shape_id'].setEnabled(True)
        #self._editable_widgets['block_id'].setEnabled(True)
        #self._editable_widgets['route_id'].setEnabled(True)
        self._editable_widgets['direction_id'].setEnabled(True)

    def save_edit(self):
        self._edit_entity.trip_headsign = self._editable_widgets['trip_headsign'].text()
        self._edit_entity.service_id = str(self._editable_widgets['service_id'].currentText())
        self._edit_entity.shape_id = str(self._editable_widgets['shape_id'].currentText())
        self._edit_entity.block_id = str(self._editable_widgets['block_id'].currentText())
        self._edit_entity.route_id = str(self._editable_widgets['route_id'].currentText())
        self._edit_entity.direction_id = int(self._editable_widgets['direction_id'].currentText())


class StopEntityView(EntityView):

    def __init__(self):
        super(StopEntityView,self).__init__()
        self._edit_entities = None # will be stop, stop_time

    def layout(self):

        box1 = QHBoxLayout()
        box2 = QHBoxLayout()
        box3 = QHBoxLayout()

        box1.addLayout(self.edit_line('stop_name'))
        box2.addLayout(self.edit_line('stop_code'))
        box3.addLayout(self.edit_time('arrival_time'))
        box3.addLayout(self.edit_time('departure_time'))
        
        self.top_widget.addLayout(box1)
        self.top_widget.addLayout(box2)
        self.top_widget.addLayout(box3)
        

    def populate(self,stop,stop_time):

        self.clear()
        self.add_data(stop,stop_time)
        self._edit_entities = (stop,stop_time)

    def add_data(self,stop,stop_time):
        self._editable_widgets['stop_name'].insert(stop.stop_name)
        self._editable_widgets['stop_code'].insert(stop.stop_code)

        arr_time = stop_time.arrival_time.split(':')
        dep_time = stop_time.departure_time.split(':')
        try:
            self._editable_widgets['arrival_time'].setTime(QTime( int(arr_time[0]),int(arr_time[1]), int(arr_time[2]) ))
        except ValueError:
            self._editable_widgets['arrival_time'].setSpecialValueText('')
        try:
            self._editable_widgets['departure_time'].setTime(QTime( int(dep_time[0]),int(dep_time[1]), int(dep_time[2]) ))
        except ValueError:
            self._editable_widgets['departure_time'].setSpecialValueText('')

        self._editable_widgets['stop_name'].setReadOnly(True)
        self._editable_widgets['stop_code'].setReadOnly(True)

        self._editable_widgets['arrival_time'].setReadOnly(True)
        self._editable_widgets['departure_time'].setReadOnly(True)


    def edit(self):
        self._editable_widgets['stop_name'].setReadOnly(False)
        self._editable_widgets['stop_code'].setReadOnly(False)

    def cancel_edit(self):
        self.clear()
        self.add_data(self._edit_entities[0],self._edit_entities[1])

    def save_edit(self):
        self._edit_entities[0].stop_name = self._editable_widgets['stop_name'].text()
        self._edit_entities[0].stop_code = self._editable_widgets['stop_code'].text()

        #self._edit_entities[1].arrival_time = self._editable_widgets['arrival_time'].time().toString()
        #self._edit_entities[1].departure_time = self._editable_widgets['departure_time'].time().toString()

class HierarchicalView(object):
    """ This is an abstract class that provides methods for creating, displaying,
    and managing the route/block -> trip -> stop view. This object will also
    have a MapView and EntityViews and will update them when the user interacts with
    the associated data entities in the hierarchy.
    """

    def __init__(self):
        self.top_widget = None
        self.gtfs = None
        self._view = None

        self.entity_top_widget = QVBoxLayout()
        self.mapview = MapView()

        self._route_entity_view = RouteEntityView()
        self._route_entity_view.top_widget = self.entity_top_widget
        self._stop_entity_view = StopEntityView()
        self._stop_entity_view.top_widget = self.entity_top_widget
        self._trip_entity_view = TripEntityView()
        self._trip_entity_view.top_widget = self.entity_top_widget

        self.entity_view = self._trip_entity_view

    def set_gtfs(self,gtfs):
        self.gtfs = gtfs
        self.mapview.set_gtfs(gtfs)
        
        self._route_entity_view.set_gtfs(gtfs)
        self._stop_entity_view.set_gtfs(gtfs)
        self._trip_entity_view.set_gtfs(gtfs)

    def set_mapview(self,mapview):
        self._mapview = mapview

    def populate(self):
        raise NotImplementedError('populate() not implemented')

    def clear(self):
        raise NotImplementedError('clear() not implemented')

    def layout(self):

        self.top_widget = QHBoxLayout()

        self.mapview.layout()

        self._stop_entity_view.layout()
        self._stop_entity_view.hide()
        self._route_entity_view.layout()
        self._route_entity_view.hide()

        # show the trip entity first
        self._trip_entity_view.layout()

    def edit(self):
        self.mapview.edit()
        self.entity_view.edit()

    def cancel_edit(self):
        self.mapview.cancel_edit()
        self.entity_view.cancel_edit()

    def save_edit(self):
        self.mapview.map_save()
        self.entity_view.save_edit()

    def display_shape(self,shape,color):
        self.mapview.clear()
        self.mapview.display_shape(shape, color)

    def display_stop(self,stop):
        self.mapview.clear_stops()
        self.mapview.display_stop(stop)

    def view_shape(self,shape,color):
        self.display_shape(shape, color)
        self.mapview.zoom_shape(shape.shape_id)

    def view_stop(self,stop):
        self.display_stop(stop)
        self.mapview.zoom_stop(stop.stop_id)

    def view_stop_and_shape(self,stop,shape,color):
        if shape:
            self.display_shape(shape, color)
            self.mapview.display_stop(stop)
        else:
            self.display_stop(stop)
        self.mapview.zoom_all()


class TreeHierarchicalView(HierarchicalView):

    def __init__(self):
        super(TreeHierarchicalView,self).__init__()
        # keep the current trip_id for getting the
        # right shape to display in the mapview
        self.current_trip_id = None

    def layout(self):
        super(TreeHierarchicalView,self).layout()
        self._tree_view = QTreeView()
        self._tree_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tree_view_model = QStandardItemModel()
        self._tree_view.setModel(self._tree_view_model)
        self.top_widget.addWidget(self._tree_view)
        self._tree_view.selectionModel().selectionChanged.connect(self.tree_selected)

    def trip_selected(self,trip_id):
        self._route_entity_view.hide()
        self._stop_entity_view.hide()
        self._trip_entity_view.show()

        trip = self.gtfs.get_trip(trip_id)
        self.current_trip_id = trip.trip_id
        shape = self.gtfs.get_shape(trip.shape_id)


        ### get color
        route = self.gtfs.get_route(trip.route_id)

        self._trip_entity_view.populate(trip)
        self.entity_view = self._trip_entity_view

        self.view_shape(shape, route.route_color)


    def stop_selected(self,trip_id,stop_id):
        self._route_entity_view.hide()
        self._trip_entity_view.hide()
        self._stop_entity_view.show()

        stop = self.gtfs.get_stop(stop_id)
        stop_time = self.gtfs.get_stop_time(trip_id,stop_id)

        self._stop_entity_view.populate(stop,stop_time)
        self.entity_view = self._stop_entity_view

        # here we ensure trip shape is shown with the stop

        if not self.current_trip_id or self.current_trip_id != trip_id:
            self.current_trip_id = trip_id
            trip = self.gtfs.get_trip(trip_id)
            route = self.gtfs.get_route(trip.route_id)
            self.view_stop_and_shape(stop,self.gtfs.get_shape(trip.shape_id),route.route_color)
            self.current_trip_id = trip_id
        else:
            self.view_stop_and_shape(stop,None,None)


class RouteTreeView(TreeHierarchicalView):

    def layout(self):
        super(RouteTreeView,self).layout()
        self._tree_view_model.setHorizontalHeaderLabels(['Route View'])

    def populate(self):
        route_label = QStandardItem('route_id')
        for route_id,route in self.gtfs.route_generator():
            route_id = str(route_id)
            route_item = QStandardItem(route_id)
            route_label.appendRow(route_item)

            trip_label = QStandardItem('trip_id')
            route_item.appendRow(trip_label)

            for trip_id,trip in self.gtfs.trip_generator(route_id):
                trip_id = str(trip_id)
                trip_item = QStandardItem(trip_id)
                trip_label.appendRow(trip_item)

                stop_label = QStandardItem('stop_id')
                trip_item.appendRow(stop_label)

                for stop_time in self.gtfs.stop_times_generator(trip_id):
                    stop_item = QStandardItem(str(stop_time.stop_id))
                    stop_label.appendRow(stop_item)
        self._tree_view_model.appendRow(route_label)

    def tree_selected(self):
        index = self._tree_view.currentIndex()
        parent_index = self._tree_view.currentIndex().parent()
        parent = self._tree_view.model().data(parent_index).toString()
        value = self._tree_view.model().data(index).toString()
        if parent == 'route_id':
            self.route_selected(value)
        elif parent == 'trip_id':
            self.trip_selected(value)
        elif parent == 'stop_id':
            trip_index = parent_index.parent()
            trip_id = self._tree_view.model().data(trip_index).toString()
            self.stop_selected(str(trip_id),str(value))
        else:
            warning('parent value not recognized')

    def route_selected(self,route_id):
        self._stop_entity_view.hide()
        self._trip_entity_view.hide()
        self._route_entity_view.show()

        route = self.gtfs.get_route(route_id)
        self._route_entity_view.populate(route)
        self.entity_view = self._route_entity_view

        self.current_trip_id = None

        self.mapview.clear()


class BlockTreeView(TreeHierarchicalView):

    def layout(self):
        super(RouteTreeView,self).layout()
        self._tree_view_model.setHorizontalHeaderLabels(['block_id','trip_id','stop_id'])

