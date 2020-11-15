# uttrs
astropy.units plus attrs


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
