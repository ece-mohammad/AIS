import pytest

from api.v1.serializers import assert_value


class ParentClass:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value


class ChildClass(ParentClass):
    ...


class DifferentClass:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value


@pytest.mark.parametrize(
    "obj, value, func, message, f_args, f_kwargs",
    [
        (1, 1, None, "", [], {}),
        (1, 1, lambda x: x, "", [], {}),
        (-1, 1, abs, "", [], {}),
        ((1, 2), (1, 2), None, "", [], {}),
        ((1, 2), (1, 2), lambda x: x, "", [], {}),
        ((1, 2), 3, sum, "", [], {}),
        ({"a": 1, "b": 2}, {"a": 1, "b": 2}, None, "", [], {}),
        ({"a": 1, "b": 2}, {"a": 1, "b": 2}, lambda x: x, "", [], {}),
        (ParentClass(1), ParentClass(1), None, "", [], {}),
        (ParentClass(1), True, isinstance, "", [ParentClass], {}),
        (ParentClass(1), ChildClass(1), None, "", [], {}),
        pytest.param(1, 2, None, "", [], {}, marks=pytest.mark.xfail),
        pytest.param(1, 2, lambda x: x, "", [], {}, marks=pytest.mark.xfail),
        pytest.param(
            DifferentClass(1),
            True,
            isinstance,
            "",
            [ParentClass],
            {},
            marks=pytest.mark.xfail,
        ),
    ],
)
def test_assert_value(obj, value, func, message, f_args, f_kwargs):
    assert_value(obj, value, func, message, *f_args, **f_kwargs)
