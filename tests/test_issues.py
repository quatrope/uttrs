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

import astropy.units as u

import attr

import numpy as np

import pytest

import uttr

# =============================================================================
# TESTS
# =============================================================================


def test_attribute_default_None():
    """https://github.com/quatrope/uttrs/issues/1"""

    @attr.s()
    class Foo:
        a = uttr.ib(default=None, unit=u.Msun)
        arr_ = uttr.array_accessor()

    foo = Foo()
    assert foo.a is None
    assert foo.arr_.a is None


def test_asdict_recursive():
    """https://github.com/quatrope/uttrs/issues/2"""

    @attr.s(frozen=True)
    class Foo:
        x = uttr.ib(unit=u.kpc)
        y = uttr.ib(unit=u.kpc)
        z = attr.ib()

        arr_ = uttr.array_accessor()

    foo = Foo(x=1, y=2, z=3)
    result = attr.asdict(foo)

    arr_ = result.pop("arr_")
    assert isinstance(arr_, uttr.ArrayAccessor)
    assert arr_.x == 1
    assert arr_.y == 2
    with pytest.raises(AttributeError):
        arr_.z

    assert result == {"x": 1 * u.kpc, "y": 2 * u.kpc, "z": 3}


def test_array_accesor_order():

    @attr.s(frozen=True)
    class Foo:
        x = uttr.ib(unit=u.kpc)
        y = uttr.ib(unit=u.kpc)
        z = uttr.ib(init=False, unit=u.kpc)

        arr_ = uttr.array_accessor()

        @z.default
        def _z_default(self):
            return self.arr_.x * self.arr_.y

    foo = Foo(x=1, y=2)

    assert np.all(foo.arr_.z == 2)
