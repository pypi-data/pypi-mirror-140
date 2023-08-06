import pytest
import platform

import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

import numpy as np
import matplotlib
# import stratigraphic_filter.stratigraphic_filter


T = 50
dt = 1
t = np.array(np.linspace(0, T, T+1//dt))


def test_pass():
    '''dummy test to give travis something to do'''
    assert True


def test_generate_elevation():
    from stratigraphic_filter.functions import generate_elevation

    mu = 0
    sigma = 1
    nt = 50
    t = np.arange(nt)
    elev = generate_elevation(t, mu, sigma)
    assert len(elev) == nt


def test_generate_stratigraphy():
    from stratigraphic_filter.functions import generate_elevation, generate_stratigraphy

    mu = 0
    sigma = 1
    nt = 50
    t = np.arange(nt)
    elev = np.arange(nt)
    strat = generate_stratigraphy(t, elev)
    assert len(strat) == nt
    assert np.all(strat == elev)
