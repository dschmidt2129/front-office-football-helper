import pytest

from coverage_assignments import (
    CoverageAssignments,
    Cover1Assignment,
    Cover2Assignment,
    Cover3CloudAssignment,
    Cover3SkyAssignment,
    Cover4Assignment,
    ManCoverageAssignment,
    Press1Assignment,
    Press2Assignment,
    Tampa2CoverageAssignment,
)


def test_base_class_assign_raises():
    base = CoverageAssignments("2 Slant (5-8)", "X(SE)", "131", "43 Regular")
    with pytest.raises(NotImplementedError):
        base.assign()


@pytest.mark.parametrize(
    "cls,route,position,off_form,def_form",
    [
        (ManCoverageAssignment, "2 Slant (5-8)", "X(SE)", "131", "43 Regular"),
        (Tampa2CoverageAssignment, "2 Slant (5-8)", "Z(FL)", "131", "43 Regular"),
        (Cover1Assignment, "8 Post (19-26)", "RB", "Weak 131", "43 Regular"),
        (Cover2Assignment, "7 Corner (19-26)", "Y", "014 ", "43 Regular"),
        (Cover3CloudAssignment, "2 Slant (5-8)", "X(SE)", "131", "43 Regular"),
        (Cover4Assignment, "2 Slant (5-8)", "X(SE)", "131", "43 Regular"),
        (Press1Assignment, "2 Slant (5-8)", "X(SE)", "131", "43 Regular"),
        (Press2Assignment, "2 Slant (5-8)", "X(SE)", "131", "43 Regular"),
    ],
)
def test_assignment_classes_return_tuple(cls, route, position, off_form, def_form):
    result = cls(route, position, off_form, def_form).assign()
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_man_coverage_unknown_position_raises():
    with pytest.raises(ValueError):
        ManCoverageAssignment("2 Slant (5-8)", "UNKNOWN", "131", "43 Regular").assign()


def test_cover3sky_assignment_currently_raises_name_error():
    with pytest.raises(NameError):
        Cover3SkyAssignment("2 Slant (5-8)", "X(SE)", "131", "43 Regular").assign()
