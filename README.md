### Prokitektura

Prokitektura is a procedural and iterative approach to generate architectural 3D models. A set of small Python functions called rules is used to generate 3D models of buildings. Each subsequent rule refines the model and adds additional details. The concept of prokitektura was inspired by CGA shape grammar developed in ETH Zurich.

Here is a brief description of the 3D model generation process on a simple example. The process starts from a 2D building outline. Its extrusion is created with the desired height. The extruded 3D shape is decomposed into a number of vertical rectangles corresponding to building facades and the upper polygon used as the base for the building roof. Floors are cut for each facade. Each floor is cut into sections with windows. Each section can be refined further.

Some parameters of the set of rules can be defined as accessible from outside. They can be changed in the Blender panel. The resulting changes in the gererated 3D model are shown interactively in the Blender 3D View window.

Prokitektura can be used to code existing buildings from a number of photos as well as to generate imaginary cities with desired styles of buildings.

An example set of prokitektura rules can be found [here](https://github.com/vvoovv/prokitektura-examples/blob/master/examples/simple01.py). The building model generated with it can be seen in the [video](http://www.youtube.com/watch?v=qmpAsEqm6mk).

The basic concepts of prokitektura are explained in the [tutorial](https://github.com/vvoovv/prokitektura-blender/wiki/Tutorial).
