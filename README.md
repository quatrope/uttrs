# uttrs

`uttrs` brinda dos utilidades principales para la creación de clases con `attrs` sensibles 
a unidades de astropy. 

- `uttr.ib` Que genera atributos sensibles a unidades.
- `uttr-array_accessor` que permite acceder a atributos con unidades y convertirlos en numpy array.

El siguiente código es un ejemplo prototipo de una clase que representa una Galaxia


```python
import attr
import uttr

import astropy.units as u

@attr.s
class Galaxy:
    x = uttr.ib(unit=u.kpc)
    y = uttr.ib(unit=u.kpc)
    z = uttr.ib(unit=u.kpc)
    
    vx = uttr.ib(unit=u.km/s)
    vy = uttr.ib(unit=u.km/s)
    vz = uttr.ib(unit=u.km/s)
    
    m = uttr.ib(unit=u.M_sun)
    
    notes = attr.ib(validator=attr.validators.instance_of(str)
    
    arr_ = uttr.array_accessor()
```
