---
title: 'Theory of the stratigraphic filter'
author:
- Andrew J. Moodie
date: \today
bibliography: refs.bib
---

## Elevation and stratigraphy

Sedimentary rocks record the conditions of Earth's surface at various times in the past.
Sediments are retained in the rock record only if they are *never* eroded at some later time.
This theory, coupled with the observation that measured sedimentation rates decreases with increasing time span measured over (often called the Sadler effect [@sadler_1981]), lead researchers to try and understand why the stratigraphy records only a vanishingly small fraction of time---in other words, the stratigraphic record is remarkably incomplete [@paola_2019].
<!-- This fact leads to the concept of *accommodation*, which is a measure of how space is available for sediment accumulation and preservation.
Accommodation is generally largest in river and delta systems, where deposition is driven by the process of migrating bedforms.
 -->
@tipper_1983 was the first to apply a random walk model to the problem of stratigraphic completeness, wherein he presented a model for how erosional events eliminate positive elevation changes from deposition, and thus preclude large periods of time from the stratigraphic record.

<!-- posited that because erosional events remove periods of time from the rock record, the averaged sedimentation rates will appear slower.  -->
Consider Figure 1, which depicts the surface elevation at a single location over time (black line), where the surface elevation  is changed by a random amount ($dz$) each timestep ($dt$); thus, the resulting  timeseries of elevation is called a *random walk*. 
The *stratigraphic filter* is the process by which periods of time (typically when the elevation was relatively high) are removed by erosive events.
Stratigraphy is calculated by finding the most recent time that the surface elevation was equal to the corresponding stratigraphic position [@schumer_2011].

![Schematic drawing of a random walk model for stratigraphic development. Each timestep the elevation is changed by adding a randomly drawn $\Delta z$ value from a probability distribution. The stratigraphy is calculated after the model run is completed, by the routine presented in the following section.](figures/schematic.png){ width=600px }

For more information, see the review of time and stratigraphy given by @paola_2019.

## Changing the distribution of the random walk
In the model, the change in elevation at a given timestep is drawn randomly from a normal distribution, with mean $\mu$ and standard deviation $\sigma$.
The random walk determined by these elevation changes is geologically analogous to a rough surface---as the surface evolves over time, even if it is simply translated in one direction, the elevation at any one location goes up and down over time, due to the surface roughness.

### Variance of elevation change
If the variability of the surface elevation were to increase, it is reasonable to expect a change in the functionality of the stratigraphic filter. 

1. Take note of the "fraction of time preserved" for the 500-run statistic: ______. 
1. How does the fraction of time preserved change when the standard deviation of the distribution is increased to $\sigma=2$: ______.
1. Does the mean bed thickness change for an increase from $\sigma=1\rightarrow\sigma=2$? Why or why not? ____________________________________________________________
___________________________________________________.
1. How does the functionality of the stratigraphic filter change when the standard deviation is decreased? Explain.__________________________________________________.


### Aggradation and "drift"
As discussed above, for sediment to be retained in the rock record, the sediment must never again be eroded.
Thus, the farther the vertical distance from deposited sediments to the active surface, the higher the chance of preservation of that sediment. 
In geologic systems, this concept is formalized by *compensation*, which is a metric of how much space is available for sediment to accumulate (at any one location this "space" is given by a vertical distance).
Over long timescales, the geologic system increases or decreases the amount of compensation at any location by a multitude of processes.
Regardless of the process, increasing compensation generally leads to *aggradation* of the surface elevation (or an increase in the surface elevation).
In the random walk model, this concept is sometimes called the model *drift*, and it can be approximated by simply changing the mean of the distribution from which $dz$ is drawn.

Experiment with how changing the mean and standard deviation each lead to variations in the behavior of the stratigraphic filter.
Record some of your observations below:
\
\
\
\


## Further discussion questions

1. How can we learn about what happened on the surface during times when there is no sediment preserved? In the model, the elevation timeseries is still known, despite the stratigraphic filter---is there any way to recover the elevation timeseries from the real rock stratigraphic record?
1. Write an algorithm (or mathematical expression) for calculating the stratigraphy $S$ from a given elevation timeseries $Z$. Both $S$ and $Z$ should be vectors that have a real number value for each timestep $t$. 

## References
