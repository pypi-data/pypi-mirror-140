---
title: 'Introduction to the rain_table model'
author:
- Andrew J. Moodie
- Jeffrey Kwang
date: 08 June 2019
bibliography: refs.bib
---

## Drainage basins

When rain falls from the atmosphere and onto the land surface, the water begins to flow, and move in a direction that is related to the sloping land surface. 
Over the length scale of a few meters, the water flows downhill.
When this process is integrated over the entire surface area of the rainfall, flows will end up intersecting and joining up, becoming larger and stronger flows; the location where the flows meet up is called a "confluence".
This causes erosion, and is the process that creates topography on landscapes.
A landscape self-organizes into a unit referred to as a "drainage basin", which is the extent of land surface that all drains to a single point.

![Schematic representation of a drainage basin, whereby flow is accumulated into channels (green). The extent of the drainage basin is all the area that flows into a defined point (the green arrow, bottom). Image from [@esham_drainage]](figures/drainage_basin.png){ width=200px }


## The numerical model

In the numerical model used in the module, the land surface is _gridded_, meaning that some unit area of the land surface has been averaged to a single value, in a regular gridded pattern, called a digital elevation model (DEM). 
The model uses the real elevation values of a series of drainage basins that flow directly into the Columbia River in Washington state, (Lat 47°10'03.8"N, Lon 120°07'31.9"W).
Flow across the surface is then routed over the DEM following the direction of "steepest descent", that is, the steepest nearby direction; because the DEM is gridded, there are eight neighboring cells to any cell, so this algorithm to flow only in the steepest direction is called D8. 

As flow from one cell joins with another cell at a confluence, the model adds the amounts in each cell together.
In this way the discharge (the amount of water conveyed in a cell) increases farther downstream in a drainage basin.
A gauge to measure discharge is simulated at the downstream end of the large drainage basin in the center of the model.
The hydrograph measured there is plotted in the bottom of the screen as a "hydrograph".


## Discussion questions

1. What assumptions about rainfall and runoff does the model make? How does this compare to what happens in the real world? (Hint: what about groundwater flow?)
1. Does the hydrograph record all of the rainfall that happens in the model? Is there a theoretical maximum value the hydrograph can possibly attain? Why or why not? 

# References