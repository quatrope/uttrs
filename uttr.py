#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Juan B Cabral
# License: BSD-3-Clause
#   Full Text: https://github.com/quatrope/uttrs/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""uttrs busca interoperar clases definidas con attrs y unidades de astropy
de manera sencilla.

"""

# =============================================================================
# IMPORTS
# =============================================================================

import astropy.units as u

import attr

import numpy as np


# =============================================================================
# CONSTANTS AND METADATA
# =============================================================================

__version__ = 0.1

UTTR_METADATA = "_uttr_ucav"


# =============================================================================
# ATTRIBUTE IMPLEMENTATION
# =============================================================================


@attr.s(frozen=True)
class UnitConverterAndValidator:
    """Conversor y validador de de astropy.units para attrs.

    Parameters
    ----------

    unit : u.UnitBase
        La unidad para asignar a los objetos sin dimension y
        validar otros objetos


    """

    unit: u.UnitBase = attr.ib(
        validator=attr.validators.instance_of(u.UnitBase)
    )

    def is_dimensionless(self, v):
        """Returns trus if v is dimensionless."""
        return (
            not isinstance(v, u.Quantity) or v.unit == u.dimensionless_unscaled
        )

    def asunit(self, value):
        """Asigna la unidad `unit` a un objeto sin dimension.

        Si el objeto ya tiene dimensión lo retorna sin modificación.

        Examples
        --------

        >>> uc = UnitConverter(u.km)

        >>> uc.asunit(1)  # dimensionless then convert
        '<Quantity 1. km>'

        >>> uc.asunit(1 * u.kpc)  # with dimension the same object is returned
        '<Quantity 1. kpc>'
        """
        if self.is_dimensionless(value):
            return value * self.unit
        return value

    def validate_is_equivalent_unit(self, instance, attribute, value):
        """Valida que el valor de un atributo sea equivalente a la unit.

        El método sigue la firma sugerida por los validadores de attrs.

        - the instance that’s being validated (aka self),
        - the attribute that it’s validating, and finally
        - the value that is passed for it.

        Raises
        ------

        ValueError:
            Si el valor tiene una dimension no equivalente a unit.

        """
        if self.is_dimensionless(value):
            return

        # creamos una solo escalar con la unidad del quantity
        # y tratamos de convertir eso. Eso evita hacer la prueba
        # con un array muy grande
        unity = 1 * value.unit
        try:
            unity.to(self.unit)
        except u.UnitConversionError:
            unit, aname, ufound = self.unit, attribute.name, value.unit
            raise ValueError(
                f"Unit of attribute '{aname}' must be equivalent to '{unit}'."
                f"Found '{ufound}'."
            )


def attribute(unit: u.UnitBase, **kwargs):
    """Crea un nuevo atributo con conversores y validadores de unidad.

    Parameters
    ----------

    unit : u.UnitBase
        La unidad para utilizar en el converter y el validator del
        atributo.
    kwargs :
        Todos los parametros extra de attr.ib()


    Ejemplo
    -------

    >>> @attr.s()
    ... class Foo:
    ...     p = unit_attribute(unit=(u.km / u.s))
    >>>> Foo(p=[1, 2, 3])
    Foo(p=<Quantity [1., 2., 3.] km / s>)


    @attr.s()
    >>> class Foo:
    ...     p = unit_attribute(unit=(u.km / u.h))

    >>> Foo(p=[1, 2, 3])
    Foo(p=<Quantity [1., 2., 3.] km / h>)

    >>> @attr.s()
    ... class Foo:
    ...     p = unit_attribute(unit=(u.km / u.s))

    >>> Foo(p=[1, 2, 3] * u.km / u.h)
    Foo(p=<Quantity [1., 2., 3.] km / h>)

    >>> Foo(p=[1, 2, 3] * u.kpc)
    ValueError: Unit of attribute 'p' must be equivalent to 'km / s'.
    Found 'kpc'.

    """
    ucav = UnitConverterAndValidator(unit=unit)

    # si ya habia validadores los saco o creo una nueva lista
    # (puede ser solo una funcion asi que lo meto a una lista)
    # para asignar mi validador de unidades
    validator = kwargs.pop("validator", [])
    if callable(validator):
        validator = [validator]
    validator.append(ucav.validate_is_equivalent_unit)

    # si habia converters lo saco
    # (puede ser solo una funcion asi que lo meto a una lista)
    # y meto ahi mi conversor al final de todo
    converter = kwargs.pop("converter", [])
    if callable(converter):
        converter = [converter]
    converter.append(ucav.asunit)

    metadata = kwargs.pop("metadata", {})
    metadata[UTTR_METADATA] = ucav

    return attr.ib(
        validator=validator, converter=converter, metadata=metadata, **kwargs
    )


#: Equivalent to `uttr.attribute` to use like "attr.ib".
ib = attribute


# =============================================================================
# ARRAY ACCESORS
# =============================================================================


@attr.s(frozen=True, repr=False)
class ArrayAccessor:
    """Convierte automaticamente los atributos tipo quantity en numpy.ndarray.

    Las instancias de ArrayAccesor (`arr_`) acceden a los atributos de
    la instancia provista, y si sonde tipo `astropy.units.Quantity` las
    convierte automaticamente en numpy.ndarray.

    Examples
    --------

    >>> @attr.s()
    ... class Foo:
    ...     quantity = attr.ib()
    ...     array = attr.ib()
    ...     string = attr.ib()

    >>> foo = Foo(
    ...     quantity=u.Quantity([1, 2]),
    ...     array=np.array([1, 2]),
    ...     string="foo"
    ... )

    >>> arr_ = ArrayAccessor(foo)

    >>> arr_
    ArrayAccessor(
        Foo(quantity=<Quantity [1., 2.]>,
        array=array([1, 2]), string='foo'))

    >>> arr_.quantity
    array([1., 2., 3.])

    >>> arr_.array
    array([1, 2, 3])

    >>> arr_.string
    'foo'

    """

    _instance = attr.ib()
    _fields_dict = attr.ib(init=False)

    @_fields_dict.default
    def _fields_dict_default(self):
        return attr.fields_dict(type(self._instance))

    def _coerce_default_unit(self, a, v):
        fd = self._fields_dict
        if a in fd and UTTR_METADATA in fd[a].metadata:
            ucav = fd[a].metadata[UTTR_METADATA]
            return v.to(ucav.unit)
        return v

    def __repr__(self):
        """repr(x) <==> x.__repr__()"""
        return f"ArrayAccessor({repr(self._instance)})"

    def __dir__(self):
        """dir(x) <==> x.__dir__()"""
        return super().__dir__() + dir(self._instance)

    def __getattr__(self, a):
        """getattr(x, y) <==> x.__getattr__(y) <==> getattr(x, y)"""
        v = getattr(self._instance, a)
        if isinstance(v, u.Quantity):
            coerced = self._coerce_default_unit(a, v)
            return np.asarray(coerced)
        return v


def array_accessor():
    """Provee un atributo ArrayAccessor a una clase attrs.

    Este nuevo atribuo, permite acceder a cualquier atributo
    o propiedad de la clase. En caso de que el valor del
    atributo sea un tipo units.Quantity, lo convierte a
    a la unidad por defecto del atributo y posteriormente
    a numpy.ndarray .

    Parameters
    ----------
    kwargs :
        Acepta todos los mismos parametros que `attr.ib` a
        ecepcion de default y factory.

    Example
    -------

    >>> @attr.s()
    ... class Foo:
    ...     q = attr.ib()
    ...     a = attr.ib()
    ...     arr_ = array_accessor()

    >>> foo = Foo(q=[1, 2, 3] * u.kg, a=np.array([1, 2, 3]))
    >>> foo
    Foo(q=<Quantity [1., 2., 3.] kg>, a=array([1, 2, 3]))

    >>> foo.q
    <Quantity [1., 2., 3.] kg>

    >>> foo.arr_.q
    array([1., 2., 3.])

    >>> foo.a
    array([1, 2, 3])

    >>> foo.arr_.a
    array([1, 2, 3])

    """
    return attr.ib(
        default=attr.Factory(ArrayAccessor, takes_self=True),
        repr=False,
        init=False,
    )
