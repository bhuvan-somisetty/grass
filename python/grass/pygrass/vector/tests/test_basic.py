"""
SPDX-FileCopyrightText: 2026 GRASS Development Team
SPDX-License-Identifier: GPL-2.0-or-later

Unit tests for grass.pygrass.vector.basic (Ilist, Cats, CatsList)
"""

from unittest.mock import patch

import pytest

from grass.pygrass.errors import GrassError
from grass.pygrass.vector.basic import Cats, CatsList, Ilist


def test_init_empty():
    """Test empty Ilist initialization."""
    ilist = Ilist()
    assert len(ilist) == 0
    assert list(ilist) == []


def test_init_with_list():
    """Test Ilist initialization with integer list."""
    ilist = Ilist([1, 2, 3])
    assert len(ilist) == 3
    assert list(ilist) == [1, 2, 3]


def test_init_with_ilist():
    """Test Ilist initialization from another Ilist instance."""
    orig = Ilist([1, 2, 3])
    ilist = Ilist(orig)
    assert len(ilist) == 3
    assert list(ilist) == [1, 2, 3]


def test_getitem():
    """Test __getitem__ with indexing and slicing."""
    ilist = Ilist([10, 20, 30, 40])
    assert ilist[0] == 10
    assert ilist[1] == 20
    assert ilist[-1] == 40
    assert ilist[1:3] == [20, 30]
    with pytest.raises(IndexError):
        _ = ilist[10]
    with pytest.raises(IndexError):
        _ = ilist[-10]


def test_setitem():
    """Test __setitem__."""
    ilist = Ilist([1, 2, 3])
    ilist[1] = 20
    assert list(ilist) == [1, 20, 3]
    with pytest.raises(ValueError, match="already in the list"):
        ilist[0] = 3


def test_contains():
    """Test contains and in operator."""
    ilist = Ilist([1, 2, 3])
    assert 1 in ilist
    assert 4 not in ilist
    assert ilist.contains(2)
    assert not ilist.contains(5)


def test_append():
    """Test appending an integer."""
    ilist = Ilist([1, 2])
    ilist.append(3)
    assert list(ilist) == [1, 2, 3]
    # Appending duplicate should not duplicate
    ilist.append(2)
    assert list(ilist) == [1, 2, 3]
    # Appending value convertible to int
    ilist.append(4.0)
    assert list(ilist) == [1, 2, 3, 4]


def test_append_error():
    """Test append raises GrassError when Vect_list_append fails."""
    ilist = Ilist()
    # Vect_list_append only fails on memory allocation failure (or NULL list),
    # which cannot be easily provoked in a unit test, so mock the return code.
    with (
        patch(
            "grass.pygrass.vector.basic.libvect.Vect_list_append",
            return_value=1,
        ),
        pytest.raises(GrassError, match="Cannot append value to list"),
    ):
        ilist.append(10)


def test_extend_with_python_list():
    """Test extending Ilist with Python list."""
    ilist = Ilist([1, 2])
    ilist.extend([3, 4])
    assert list(ilist) == [1, 2, 3, 4]


def test_extend_with_ilist():
    """Test extending Ilist with another Ilist instance."""
    ilist_a = Ilist([1, 2, 3])
    ilist_b = Ilist([4, 5, 6])
    ilist_a.extend(ilist_b)
    assert list(ilist_a) == [1, 2, 3, 4, 5, 6]


def test_remove_int():
    """Test removing an integer."""
    ilist = Ilist([1, 2, 3, 4])
    ilist.remove(2)
    assert list(ilist) == [1, 3, 4]


def test_remove_ilist():
    """Test removing items from another Ilist instance."""
    ilist_a = Ilist([1, 2, 3, 4, 5])
    ilist_b = Ilist([2, 4])
    ilist_a.remove(ilist_b)
    assert list(ilist_a) == [1, 3, 5]


def test_remove_iterable():
    """Test removing items with an iterable."""
    ilist = Ilist([1, 2, 3, 4, 5])
    ilist.remove([1, 3])
    assert list(ilist) == [2, 4, 5]


def test_remove_invalid():
    """Test removing unsupported value type raises ValueError."""
    ilist = Ilist([1, 2])
    # Pass non-iterable types so execution reaches the unsupported type branch
    with pytest.raises(ValueError, match="is not supported"):
        ilist.remove(1.5)
    with pytest.raises(ValueError, match="is not supported"):
        ilist.remove(None)


def test_reset():
    """Test resetting Ilist."""
    ilist = Ilist([1, 2, 3])
    ilist.reset()
    assert len(ilist) == 0
    assert list(ilist) == []


def test_repr():
    """Test __repr__."""
    ilist = Ilist([1, 2, 3])
    assert repr(ilist) == "Ilist([1, 2, 3])"


def test_cats_init_empty():
    """Test empty Cats initialization."""
    cats = Cats()
    assert len(cats) == 0
    assert cats.cat == []
    assert cats.layer == []


def test_cats_set_and_get():
    """Test setting and getting categories in Cats."""
    cats = Cats()
    cats.set(0, layer=1)
    cats.set(10, layer=1)
    cats.set(20, layer=2)
    assert len(cats) == 3
    assert cats.cat == [0, 10, 20]
    assert cats.layer == [1, 1, 2]

    first_cat, n_found = cats.get(layer=1)
    assert first_cat == 0
    assert n_found == 2

    first_cat_l2, n_found_l2 = cats.get(layer=2)
    assert first_cat_l2 == 20
    assert n_found_l2 == 1


def test_cats_delete_zero():
    """Test deleting category 0 does not delete other categories."""
    cats = Cats()
    cats.set(0, layer=1)
    cats.set(1, layer=1)
    cats.set(2, layer=1)
    assert len(cats) == 3

    cats.delete(0, layer=1)
    assert len(cats) == 2
    assert cats.cat == [1, 2]
    assert cats.layer == [1, 1]


def test_cats_delete_nonexistent_zero():
    """Test deleting category 0 when absent raises ValueError."""
    cats = Cats()
    cats.set(1, layer=1)
    with pytest.raises(ValueError, match="category\\(0\\) number does not exist"):
        cats.delete(0, layer=1)
    assert cats.cat == [1]


def test_cats_delete_all_layer():
    """Test deleting all categories of a layer when cat is None."""
    cats = Cats()
    cats.set(1, layer=1)
    cats.set(2, layer=1)
    cats.set(10, layer=2)
    cats.delete(layer=1)
    assert len(cats) == 1
    assert cats.cat == [10]
    assert cats.layer == [2]


def test_cats_delete_nonexistent_layer():
    """Test deleting from nonexistent layer raises ValueError."""
    cats = Cats()
    with pytest.raises(ValueError, match="does not exist"):
        cats.delete(layer=99)


def test_cats_contains_and_len():
    """Test Cats __contains__ and __len__."""
    cats = Cats()
    cats.set(0, layer=1)
    cats.set(5, layer=1)
    assert len(cats) == 2
    assert 0 in cats
    assert 5 in cats
    assert 99 not in cats


def test_cats_reset():
    """Test resetting Cats."""
    cats = Cats()
    cats.set(0, layer=1)
    cats.set(1, layer=1)
    cats.reset()
    assert len(cats) == 0
    assert cats.cat == []
    assert cats.layer == []


def test_cats_repr():
    """Test Cats __repr__."""
    cats = Cats()
    cats.set(1, layer=1)
    assert repr(cats) == "Cats([(1, 1)])"


def test_cats_get_list():
    """Test Cats.get_list returns an Ilist."""
    cats = Cats()
    cats.set(0, layer=1)
    cats.set(5, layer=1)
    ilist = cats.get_list(layer=1)
    assert list(ilist) == [0, 5]

    with pytest.raises(ValueError, match="does not exist"):
        cats.get_list(layer=-1)


def test_catslist_init():
    """Test CatsList initialization."""
    cl = CatsList()
    assert len(cl) == 0
    assert cl.n_ranges == 0
    assert cl.min == []
    assert cl.max == []


def test_catslist_from_string():
    """Test CatsList.from_string."""
    cl = CatsList()
    cl.from_string("2,3,5-9,20")
    assert cl.min == [2, 3, 5, 20]
    assert cl.max == [2, 3, 9, 20]
    assert len(cl) == 4
    assert 2 in cl
    assert 7 in cl
    assert 10 not in cl


def test_catslist_from_array():
    """Test CatsList.from_array."""
    cl = CatsList()
    cl.from_array([1, 2, 3, 5, 6, 7])
    assert cl.min == [1, 5]
    assert cl.max == [3, 7]
    assert len(cl) == 2
    assert 2 in cl
    assert 6 in cl
    assert 4 not in cl


def test_catslist_repr():
    """Test CatsList __repr__."""
    cl = CatsList()
    cl.from_string("1-3")
    assert repr(cl) == "CatsList(ranges=[(1, 3)], layer=0)"
