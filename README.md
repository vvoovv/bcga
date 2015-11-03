### BCGA (Computer Generated Architecture for Blender)

BCGA is a procedural and iterative approach to generate architectural 3D models. A set of small Python functions called rules is used to generate 3D models of buildings. Each subsequent rule refines the model and adds additional details. The concept of prokitektura was inspired by CGA shape grammar developed in ETH Zurich.

Here is a brief description of the 3D model generation process on a simple example. The process starts from a 2D building outline. Its extrusion is created with the desired height. The extruded 3D shape is decomposed into a number of vertical rectangles corresponding to building facades and the upper polygon used as the base for the building roof. Floors are cut for each facade. Each floor is cut into sections with windows. Each section can be refined further.

Some parameters of the set of rules can be defined as accessible from outside. They can be changed in the Blender panel. The resulting changes in the gererated 3D model are shown interactively in the Blender 3D View window.

Prokitektura can be used to code existing buildings from a number of photos as well as to generate imaginary cities with desired styles of buildings.

Example sets of prokitektura rules:
* [simple01.py](https://github.com/vvoovv/prokitektura-examples/blob/master/examples/simple01.py), [video](https://www.youtube.com/watch?v=GixKhqrdANs)
* [house_01.py](https://github.com/vvoovv/prokitektura-examples/blob/master/examples/house_01.py), [video](http://www.youtube.com/watch?v=ZJDHtPAF9d8)

The basic concepts of BCGA are explained in the [tutorial](https://github.com/vvoovv/bcga/wiki/Tutorial).

twitter: [@prokitektura](https://twitter.com/prokitektura)

Thread at blenderartists.org: http://blenderartists.org/forum/showthread.php?351081-Addon-BCGA-Computer-Generated-Architecture-for-Blender-3D-buildings-with-Python


## Donations
If you like BCGA, please consider making a donation:

[![Please donate](https://www.paypalobjects.com/en_US/GB/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ZZ7CHNYKWYYZE)
