#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Juan B Cabral
# License: BSD-3-Clause
#   Full Text: https://github.com/quatrope/uttrs/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""uttrs seeks to interoperate Classes definided using attrs and astropy units
in a simple manner.

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
    """Converter and validator of astropy.units for attrs.

    Parameters
    ----------

    unit : u.UnitBase
        The base units for attribute default unit assignation and validation
        of inputs


    """

    unit: u.UnitBase = attr.ib(
        validator=attr.validators.instance_of(u.UnitBase)
    )

    def is_dimensionless(self, v):
        """Returns true if v is dimensionless."""
        return (
            not isinstance(v, u.Quantity) or v.unit == u.dimensionless_unscaled
        )

    def asunit(self, value):
        """Assigns `unit` to a dimensionless object.

        If the object already has a dimension it returns it without change

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
        """Validates that the attribute value is equivalent to the
        configured unit.

        This method follows the suggested signature by attrs validators.

        - the instance that’s being validated (aka self),
        - the attribute that it’s validating, and finally
        - the value that is passed for it.

        Raises
        ------

        ValueError:
            If the value has a non-equivalent dimesion to unit.

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
    """Creats a new attribute with converters and unit validators.

    Parameters
    ----------

    unit : u.UnitBase
        The unit to use in the converters and the attribute validator
    kwargs :
        Extra parameter of attr.ib()


    Example
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
    """Provides an ArrayAccessor attribute to an attrs class.

    This new attribute allows access to any other attribute or property of
    the class. In the case that the value given to the attribute is a
    `units.Quantity` type, it converts it to the default unit of the attribute
    and aftwerwars to a `numpy.ndarray`.

    Parameters
    ----------
    kwargs :
        Accepts every parameter that `attr.ib` can accept, except for
        default and factory.

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
