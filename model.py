#This is a full wrapper around any third-party GTFS API

import transitfeed


class GTFSModel:
	""" Provides functionality for the view in accessing GTFS data
	from a given library - in this case transitfeed. 
	This may eventually be a true wrapper around
	transitfeed. But for now, the view is using transitfeed
	objects.
	"""

	def __init__(self):
		self.gtfs = None
		self.file = None

	def load(self,gtfs_file_name):
		self.gtfs = transitfeed.Schedule()
		self.gtfs.Load(str(gtfs_file_name))

	def export(self,gtfs_file_name):
		self.gtfs.WriteGoogleTransitFeed(str(gtfs_file_name))

	def store(self):
		pass

	def export(self,gtfs_file_name):
		if self.gtfs:
			self.gtfs.WriteGoogleTransitFeed(gtfs_file_name)

	def get_route(self,route_id):
		return self.gtfs.GetRoute(str(route_id))

	def get_trip(self,trip_id):
		return self.gtfs.GetTrip(str(trip_id))

	def get_shape(self,shape_id):
		return self.gtfs.GetShape(str(shape_id))

	def get_stop(self,stop_id):
		return self.gtfs.GetStop(str(stop_id))

	def get_block_ids(self):
		return sorted(list(set([trip.block_id for trip in self.gtfs.trips.values()])))

	def get_service_ids(self):
		return sorted(set([trip.service_id for trip in self.gtfs.trips.values()]))

	def get_route_ids(self):
		return sorted(list(set(self.gtfs.routes.keys())))

	def get_shape_ids(self):
		return sorted(list(set(self.gtfs._shapes.keys())))

	def get_stop_time(self,trip_id,stop_id):
		for stop_time in self.gtfs.GetTrip(trip_id).GetStopTimes():
			if stop_time.stop_id == stop_id:
				return stop_time

	def modify_shape_points(self,shape_id,shape_points):
		"""shape_points = [[lat,long],[lat,long]
		"""
		shape = self.get_shape(shape_id)
		shape.ClearPoints()
		for p in shape_points:
			shape.AddPoint(p[0],p[1])
		

	def modify_stop_point(self,stop_id,point):
		"""Assumes point is [float,float]
		"""
		stop = self.get_stop(stop_id)
		stop.stop_lat = point[0]
		stop.stop_lon = point[1]

	def route_generator(self):
		for route_id, route in self.gtfs.routes.items():
			yield route_id, route

	def trip_generator(self,route_id):
		route = self.get_route(route_id)
		for trip in route.trips:
			yield trip.trip_id,trip

	def stop_times_generator(self,trip_id):
		for stop_time in self.get_trip(trip_id).GetStopTimes():
			yield stop_time
