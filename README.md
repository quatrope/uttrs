# uttrs

`uttrs` seeks to interoperate Classes definided using attrs and *astropy units* in a simple manner.

![img](res/ugly_logo.png)

[![Build Status](https://travis-ci.com/quatrope/uttrs.svg?branch=main)](https://travis-ci.com/quatrope/uttrs)
[![License](https://img.shields.io/pypi/l/uttrs?color=blue)](https://tldrlegal.com/license/bsd-3-clause-license-(revised))
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://badge.fury.io/py/uttrs)

**uttrs** is mainly two functions:

- `uttr.ib` which generates attributes sensitive to units.
- `uttr.array_accessor` which allows access to attributes linked to units, and transform them into numpy arrays.

## Installing

- From PyPI

```s
$ pip install uttrs
```

- Simply clone and from within the repo

```s
$ pip install -e .
```


## Quick Start

The following piece of code is an example prototype of a Class representing a Galaxy.
The Galaxy contains:

- three arrays (`x`, `y`, `z`) with particle positions, measured in *kiloparsecs* (`u.kpc`).
- three arrays (`vx`, `vy`, `vz`) for the particle velocities, measured in *Km/s* (`u.kms/u.s`).
- an array (`m`) of particle masses, expressed in *solar masses* (`u.M_sun`).
- a free text for note taking in `notes`.

In every case we would like to access to position, velocity and mass of the particles, with and without units (as `np.ndarray`).
Suggested units in the information of the attributes behave like this:

- If the user makes the class instance without unit specification then default assumed unit is used.
- If, otherwise, another unit is used as input, it is validated the feasibility of the conversion to default unit.

```python
import attr
import uttr

import astropy.units as u

@attr.s
class Galaxy:
    x = uttr.ib(unit=u.kpc)
    y = uttr.ib(unit=u.kpc)
    z = uttr.ib(unit=u.kpc)

    vx = uttr.ib(unit=u.km/u.s)
    vy = uttr.ib(unit=u.km/u.s)
    vz = uttr.ib(unit=u.km/u.s)

    m = uttr.ib(unit=u.M_sun)

    notes = attr.ib(validator=attr.validators.instance_of(str))

    arr_ = uttr.array_accessor()
```

## Creating a galaxy

```python
>>> import numpy as np
>>> import astropy.units as u

# Creating the particle arrays
>>> x = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)
>>> y = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)
>>> z = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)
>>> vx = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)
>>> vy = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)
>>> vz = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)
>>> m = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)

>>> gal = Galaxy(
...     x = x * u.kpc,  # kpc is the suggested unit
...     y = y * u.mpc,  # mpc is equivalent to kpc
...     z = z,  # we assume is the suggested kpc unit
...     vx = vx * (u.km/u.s), # the suggested unit
...     vy = vy * (u.km/u.s), # the suggested unit
...     vz = vz, # the suggested unit
...     m = m * u.M_sun, # the suggested unit
...     notes="a random galaxy made with random numbers")

>>> gal
Galaxy(
    x=<Quantity [5632.35740606, 1363.36235923, 3037.46794044, 2785.45299727, 2515.35793673] kpc>,
    y=<Quantity [4457.3573917 , 2873.54575512, 7979.68745148, 5930.55394614, 5903.63598164] mpc>,
    z=<Quantity [6122.35929872, 3740.22821927, 6859.42245056, 7119.8256744 , 3632.74980958] kpc>,
    vx=<Quantity [7141.40469733, 5713.29552487, 5000.535142  , 9366.36402447, 2967.2546077 ] km / s>,
    vy=<Quantity [8514.83018331, 1362.13309457, 1136.30959053, 1985.49551226, 3286.69029298] km / s>,
    vz=<Quantity [6218.56279077, 2015.04638043, 9919.99579782, 1278.94359767, 7228.21626876] km / s>,
    m=<Quantity [5640.62516958, 4070.66620947, 6106.583697  , 4063.39917315, 3028.85393523] solMass>,
    notes='a random galaxy made with random numbers')

# we can access al the attributes in the traditional python way
>>> gal.x
<Quantity [5632.35740606, 1363.36235923, 3037.46794044, 2785.45299727, 2515.35793673] kpc>

>>> gal.vz  # z is now a km/s
<Quantity [6218.56279077, 2015.04638043, 9919.99579782, 1278.94359767, 7228.21626876] km / s>

# We stored y as mpc
>>> gal.y
<Quantity [8093.44916403, 2198.55398718, 5464.79397835, 1860.72260272, 3636.64010118] mpc>

```


## Simple interaction with `numpy.ndarray`

We can access all the same attributes declared with `uttr.ib but` coerced to the default unit as numpy array.

```python
>>> gal.arr_.y
array([0.00809345, 0.00219855, 0.00546479, 0.00186072, 0.00363664])
```

The above code is equivalent to

```python
>>> np.asarray(gal.y.to(u.kpc))
array([0.00809345, 0.00219855, 0.00546479, 0.00186072, 0.00363664])
```

## Equivalent units errors

If we change the unit to something not equivalent to the default unit
declares in `uttr.ib` an exception is raised.

Lets fot example define `x` as a kilogram (`u.kg`)

```python
>>> gal = Galaxy(
...     x = x * u.kg,  # kg is not equivalent to kpc
...     y = y,
...     z = z,
...     vx = vx,
...     vy = vy,
...     vz = vz,
...     m = m,
...     notes="a random galaxy made with random numbers")

ValueError: Unit of attribute 'x' must be equivalent to 'kpc'.Found 'kg'.
```


## References

### Astropy

>  Price-Whelan, Adrian M., et al. "The Astropy project:
   Building an open-science project and status of the v2. 0 core
   package." The Astronomical Journal 156.3 (2018): 123.