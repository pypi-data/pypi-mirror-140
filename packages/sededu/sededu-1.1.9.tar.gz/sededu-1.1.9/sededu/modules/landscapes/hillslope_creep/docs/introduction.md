---
title: 'Introduction to the hillslope creep model'
author:
- Andrew J. Moodie
date: 10 June 2019
bibliography: refs.bib
---

## Hillslopes

The evolution of landscapes begins at the hillslope. 
Gravity is always acting on a hillslope, causing a force directed in the direction of the slope.
Over time, tiny slips of soil particles past one another driven by this force, in the direction of the slope, causes _soil creep_ or _hillslope creep_.
Hillslope creep is a _diffusive_ process, meaning that it works to reduce gradients over space.
In the case of the landscape, the gradient is the elevation, and so creep works to change steep slopes (i.e., large gradients in elevation) into smooth and gradual gradients or eventually even no gradient at all (i.e., a flat landscape).
So creep works to smooth landscapes over time.

![A landscape that has been subject to hillslope creep. Credit [@hobley].](figures/hillslope_creep.jpeg){ width=600px }


## The numerical model

In this module, we will look at this diffusive process of hillslope creep in cross-section, that is, as a slice though the hillslope.
If we start by defining the elevation by a coordinate $z$, and the along-slope coordinate as $x$, we have the slope given by $dz/dx$ (i.e., rise/run).

The diffusive process of hillslope creep can be modeled as:
$$\frac{\partial z}{\partial t} = \frac{\partial}{\partial x} \left( -K \frac{\partial z}{\partial x} \right)$$
where ($-K(\partial z/\partial x)$) is defined to be the sediment flux down the hillslope ($q_s$), $t$ is time, and $K$ is a diffusivity coefficient, which relates the slope to sediment flux.

![Schematic representation of a hillslope, discretized to show how the hillslope is evolved by sediment flux calculations. See text for explanation.](figures/hillslope_drawing.png){ width=400px }

This equation can be explained in words as: the change in elevation ($z$) over time $t$ is equivalent to the divergence in sediment flux ($q_s$) down the hillslope ($x$).


## Discussion questions

1. You can control the downcutting rate at the downslope end of the model. What drives this rate in the real landscape? Where does the sediment leaving the model at the downslope end go in a real landscape?  
1. What would you change about the model to make it more realistic?

## References
