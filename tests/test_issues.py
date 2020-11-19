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
