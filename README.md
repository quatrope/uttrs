# uttrs

`uttrs` brinda dos utilidades principales para la creación de clases con `attrs` sensibles 
a unidades de astropy. 

- `uttr.ib` Que genera atributos sensibles a unidades.
- `uttr-array_accessor` que permite acceder a atributos con unidades y convertirlos en numpy array.

El siguiente código es un ejemplo prototipo de una clase que representa una Galaxia. 
La galaxia tiene 

- tres arreglos (`x`, `y`, `z`) de las posiciones de sus particulas las cuales se miden en kiloparsecs (`u.kpc`).
- tres arreglos (`vx`, `vy`, `vz`) de las velocidades de sus particulas las cuales se miden en $Km/s$ (`u.kms/s`).
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
    
    vx = uttr.ib(unit=u.km/s)
    vy = uttr.ib(unit=u.km/s)
    vz = uttr.ib(unit=u.km/s)
    
    m = uttr.ib(unit=u.M_sun)
    
    notes = attr.ib(validator=attr.validators.instance_of(str)
    
    arr_ = uttr.array_accessor()
```
