TripBlazer is a desktop application under development that aims to make viewing, editing, and (eventually) creating General Transit Feed Specification (GTFS) data convenient and intuitive.


A trip_id selected:
![alt tag](https://raw.github.com/TripBlazer/TripBlazer/master/screenshots/trip-selected.png)

A trip being edited, including its shape:
![alt tag](https://raw.github.com/TripBlazer/TripBlazer/master/screenshots/shape-editing.png)

A stop being edited:
![alt tag](https://raw.github.com/TripBlazer/TripBlazer/master/screenshots/stop-editing.png)


Wishlist:
1) Add automated testing and ensure changes to GTFS data objects maintain dataset integrity. 
2) Database support for large GTFS sets. SQLite might be a solution.
3) Transition from Google Maps API to Leaflet, if possible, and optimize performance for map editing.
4) Simplify GTFS in-memory model and validator. Aim for less code = easier compilation and packaging.
5) More stylish interface using QML.
6) Add block view (top level parent is block instead of route). 
7) Display HTML page generated from the transitfeed validator.
