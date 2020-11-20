#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Juan B Cabral and QuatroPe.
# License: BSD-3-Clause
#   Full Text: https://github.com/quatrope/uttrs/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""test for uttr

"""

# =============================================================================
# IMPORTS
# =============================================================================

import unittest.mock as mock

import astropy.units as u

import attr

import numpy as np

import pytest

import uttr

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def make_ucav():
    def make(unit):
        return uttr.UnitConverterAndValidator(unit=unit)

    return make


@pytest.fixture
def attribute():
    class Attribute:
        pass

    attribute = Attribute()
    attribute.name = "foo"
    return attribute


@pytest.fixture(scope="session")
def make_cls():
    def make(name="Foo", **kwargs):
        return attr.make_class(name, kwargs)

    return make


# =============================================================================
# TESTS
# =============================================================================


class TestUnitConverterAndValidator:
    def test_is_dimensionless(self, make_ucav):
        ucav = make_ucav(u.kg)
        assert ucav.is_dimensionless([1, 2, 3])
        assert ucav.is_dimensionless(1)
        assert not ucav.is_dimensionless([1, 2, 3] * u.kg)
        assert not ucav.is_dimensionless(1 * u.kg)

    def test_convert_quantity(self, make_ucav):
        ucav = make_ucav(u.kg)
        assert ucav.convert_quantity(1 * u.kg) == 1 * u.kg
        assert ucav.convert_quantity(1 * u.g) == 0.001 * u.kg

        arr = [1, 2, 3] * u.g
        np.testing.assert_array_equal(
            ucav.convert_quantity(arr), [0.001, 0.002, 0.003] * u.kg
        )
        with pytest.raises(u.UnitConversionError):
            ucav.convert_quantity(1 * u.m)

        with pytest.raises(AttributeError):
            ucav.convert_quantity(1)

        with pytest.raises(AttributeError):
            ucav.convert_quantity([1])

        with pytest.raises(AttributeError):
            ucav.convert_quantity(np.array([1]))

    def test_convert_if_dimensionless(self, make_ucav):
        ucav = make_ucav(u.kg)
        assert ucav.convert_if_dimensionless(1).unit == u.kg
        assert ucav.convert_if_dimensionless(1 * u.kg).unit == u.kg
        assert ucav.convert_if_dimensionless(1 * u.m).unit == u.m

        arr = [1, 2, 3] * u.kg
        assert ucav.convert_if_dimensionless(arr) is arr

    def test_validate_is_equivalent_unit(self, make_ucav, attribute):
        ucav = make_ucav(u.kg)
        assert ucav.validate_is_equivalent_unit(None, attribute, 1) is None
        assert ucav.validate_is_equivalent_unit(None, attribute, [1]) is None

        assert (
            ucav.validate_is_equivalent_unit(None, attribute, 1 * u.g) is None
        )
        assert (
            ucav.validate_is_equivalent_unit(None, attribute, 1 * u.kg) is None
        )
        assert (
            ucav.validate_is_equivalent_unit(None, attribute, 1 * u.M_sun)
            is None
        )

        with pytest.raises(ValueError):
            ucav.validate_is_equivalent_unit(None, attribute, 1 * u.m)


class TestAttributeFunction:
    def test_converter(self, make_cls):
        with mock.patch(
            "uttr.UnitConverterAndValidator.convert_if_dimensionless"
        ) as asunit:
            Cls = make_cls(foo=uttr.ib(unit=u.kg))

            # check the converter
            asunit.assert_not_called()
            Cls(foo="foo")
            asunit.assert_called_once_with("foo")

    def test_converter_with_another(self, make_cls):
        def fake_converter(v):
            return v

        with mock.patch(
            "uttr.UnitConverterAndValidator.convert_if_dimensionless"
        ) as asunit:
            Cls = make_cls(foo=uttr.ib(unit=u.kg, converter=fake_converter))

            # check the converter
            asunit.assert_not_called()
            Cls(foo="foo")
            asunit.assert_called_once_with("foo")

    def test_validator(self, make_cls):
        with mock.patch(
            "uttr.UnitConverterAndValidator.validate_is_equivalent_unit"
        ) as validator:
            Cls = make_cls(foo=uttr.ib(unit=u.kg))
            attribute = attr.fields(Cls).foo

            validator.assert_not_called()
            instance = Cls(foo=1)
            validator.assert_called_once_with(instance, attribute, 1 * u.kg)

    def test_validator_with_another(self, make_cls):
        def fake_validator(*args, **kwargs):
            pass

        with mock.patch(
            "uttr.UnitConverterAndValidator.validate_is_equivalent_unit"
        ) as validator:
            Cls = make_cls(foo=uttr.ib(unit=u.kg, validator=fake_validator))
            attribute = attr.fields(Cls).foo

            validator.assert_not_called()
            instance = Cls(foo=1)
            validator.assert_called_once_with(instance, attribute, 1 * u.kg)

    def test_metadata(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg))
        attribute = attr.fields(Cls).foo

        assert uttr.UTTR_METADATA in attribute.metadata

        ucav = attribute.metadata[uttr.UTTR_METADATA]
        assert isinstance(ucav, uttr.UnitConverterAndValidator)
        assert ucav.unit is u.kg

    def test_auto_conversion(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg))
        instance = Cls(foo=1)
        assert instance.foo == 1 * u.kg

    def test_same_unit(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg))
        instance = Cls(foo=1 * u.kg)
        assert instance.foo == 1 * u.kg

    def test_equivalent_unit(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg))
        instance = Cls(foo=1 * u.g)
        assert instance.foo == 1 * u.g

    def test_invalie_unit(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg))
        with pytest.raises(ValueError):
            Cls(foo=1 * u.m)


class TestArrayAccessor:
    def test_dimensionless_access(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg))
        instance = Cls(foo=1)
        arr_ = uttr.ArrayAccessor(instance)

        assert instance.foo == 1 * u.kg
        assert arr_.foo == 1

    def test_equivalent_access(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg))
        instance = Cls(foo=1 * u.g)
        arr_ = uttr.ArrayAccessor(instance)

        assert instance.foo == 1 * u.g
        assert arr_.foo == 0.001

    def test_same_unit_access(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg))
        instance = Cls(foo=1 * u.kg)
        arr_ = uttr.ArrayAccessor(instance)

        assert instance.foo == 1 * u.kg
        assert arr_.foo == 1

    def test_no_uttr_access(self, make_cls):
        Cls = make_cls(foo=attr.ib())
        instance = Cls(foo="foo")
        arr_ = uttr.ArrayAccessor(instance)

        assert instance.foo == "foo"
        with pytest.raises(AttributeError):
            arr_.foo

    def test_no_uttr_quantity(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg))
        instance = Cls(foo=1 * u.kg)
        instance.faa = 1 * u.kpc

        arr_ = uttr.ArrayAccessor(instance)

        assert instance.faa == 1 * u.kpc
        with pytest.raises(AttributeError):
            assert arr_.faa

    def test_repr(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg))
        instance = Cls(foo=1 * u.kg)
        arr_ = uttr.ArrayAccessor(instance)

        assert repr(arr_) == f"ArrayAccessor({repr(instance)})"

    def test_dir(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg))
        instance = Cls(foo=1 * u.kg)
        arr_ = uttr.ArrayAccessor(instance)
        expected = super(uttr.ArrayAccessor, arr_).__dir__() + dir(instance)

        assert sorted(dir(arr_)) == sorted(expected)

    def test_attrs_quantity(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg), faa=attr.ib())
        instance = Cls(foo=1 * u.kg, faa=1 * u.kg)
        arr_ = uttr.ArrayAccessor(instance)

        assert instance.foo == 1 * u.kg
        assert arr_.foo == 1

        assert instance.faa == 1 * u.kg
        with pytest.raises(AttributeError):
            arr_.faa


class TestArrayAccessorFunction:
    def test_dimensionless_access(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg), arr_=uttr.array_accessor())
        instance = Cls(foo=1)

        assert instance.foo == 1 * u.kg
        assert instance.arr_.foo == 1

    def test_equivalent_access(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg), arr_=uttr.array_accessor())
        instance = Cls(foo=1 * u.g)

        assert instance.foo == 1 * u.g
        assert instance.arr_.foo == 0.001

    def test_same_unit_access(self, make_cls):
        Cls = make_cls(foo=uttr.ib(unit=u.kg), arr_=uttr.array_accessor())
        instance = Cls(foo=1 * u.kg)

        assert instance.foo == 1 * u.kg
        assert instance.arr_.foo == 1

    def test_no_uttr_access(self, make_cls):
        Cls = make_cls(foo=attr.ib(), arr_=uttr.array_accessor())
        instance = Cls(foo="foo")

        assert instance.foo == "foo"

        with pytest.raises(AttributeError):
            instance.arr_.foo

    def test_no_uttr_quantity(self, make_cls):
        Cls = make_cls(foo=attr.ib(), arr_=uttr.array_accessor())
        instance = Cls(foo=1 * u.kg)

        assert instance.foo == 1 * u.kg

        with pytest.raises(AttributeError):
            instance.arr_.foo
