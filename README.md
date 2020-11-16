# uttrs

`uttrs` brinda dos utilidades principales para la creación de clases con `attrs` sensibles a unidades de astropy.

![img](res/ugly_logo.png)

- `uttr.ib` Que genera atributos sensibles a unidades.
- `uttr-array_accessor` que permite acceder a atributos con unidades y convertirlos en numpy array.

El siguiente código es un ejemplo prototipo de una clase que representa una Galaxia.
La galaxia tiene

- tres arreglos (`x`, `y`, `z`) de las posiciones de sus particulas las cuales se miden en kiloparsecs (`u.kpc`).
- tres arreglos (`vx`, `vy`, `vz`) de las velocidades de sus particulas las cuales se miden en $Km/s$ (`u.kms/u.s`).
- Un arreglos (`m`) de las mases de sus particulas las cuales se miden en masas solares (`u.M_sun`).
- Un texto libre para notas `notes`

En todos los casos se desea poder acceder a las velocidade, posiciones y masas; con y sin unidades (como `np.ndarray`)
Las unidades sugeridas en la información de las particulas son sugerencias asi:

- Si el usuario ingresa la informacón sin unidades, la galaxia asume que estan en la unida sugerida.
- Si ingresa en alguna otra unidad valida que se equivalente a la unidad sugerida.


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

## Creemos una galaxia

```pycon
>>> import numpy as np
>>> import astropy.units as u

# creamos las particulas
>>> x = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)
>>> y = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)
>>> z = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)
>>> vx = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)
>>> vy = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)
>>> vz = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)
>>> m = np.random.randint(1000, 10_000, size=5) + np.random.rand(5)

>>> gal = Galaxy(
...     x = x * u.kpc,  # kpc is the sugested unit
...     y = y * u.mpc,  # mpc is equivalent to kpc
...     z = z,  # we asume is the sugested kpc unit
...     vx = vx * (u.km/u.s), # the sugested unit
...     vy = vy * (u.km/u.s), # the sugested unit
...     vz = vz, # the sugested unit
...     m = m * u.M_sun, # the sugested unit
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


## Simple interacción con `numpy.ndarray`

we can access all the same attributes declared with `uttr.ib but` coerced to the default unit as numpy array.

```pycon
>>> gal.arr_.y
array([0.00809345, 0.00219855, 0.00546479, 0.00186072, 0.00363664])
```

The above code is equivalent to

```pycon
>>> np.asarray(gal.y.to(u.kpc))
array([0.00809345, 0.00219855, 0.00546479, 0.00186072, 0.00363664])
```

## Equivalent units errors

If we change the unit to something not equivalent to the default unit
declares in `uttr.ib` an exception is raised.

Lets fot exaple define `x` as a kilogram (`u.kg`)

```pycon
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
