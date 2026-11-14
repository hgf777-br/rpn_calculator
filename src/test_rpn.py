import math
from decimal import Decimal

import pytest

import rpn


@pytest.fixture
def RPN(qtbot):
    pyrpn_window = rpn.PyRpnWindow()
    pyrpn_window.show()

    return rpn.PyRpn(pyrpn_window, rpn.PyRpnEvaluate(pyrpn_window))


def test_new(RPN):
    RPN._view.btn_one.click()

    assert RPN._model._stack.peek_x() == Decimal(1)


def test_two_args_integer_operations(qtbot):
    pyrpn_window = rpn.PyRpnWindow()
    rpn_obj = rpn.PyRpnEvaluate(pyrpn_window)

    # add operation
    rpn_obj._stack.push(Decimal(7))
    rpn_obj._stack.push(Decimal(3))
    rpn_obj.btn_operation_two_arg('+')
    assert rpn_obj._stack.peek_x() == Decimal(10)

    # subtract operation
    rpn_obj._stack.push(Decimal(4))
    rpn_obj.btn_operation_two_arg('-')
    assert rpn_obj._stack.peek_x() == Decimal(6)

    # multiply operation
    rpn_obj._stack.push(Decimal(3))
    rpn_obj.btn_operation_two_arg('*')
    assert rpn_obj._stack.peek_x() == Decimal(18)

    # multiply operation
    rpn_obj._stack.push(Decimal(6))
    rpn_obj.btn_operation_two_arg('/')
    assert rpn_obj._stack.peek_x() == Decimal(3)

    # y expoent x operation
    rpn_obj._stack.push(Decimal(3))
    rpn_obj.btn_operation_two_arg('y^x')
    assert rpn_obj._stack.peek_x() == Decimal(27)

    # mod operation
    rpn_obj._stack.push(Decimal(7))
    rpn_obj.btn_operation_two_arg('mod')
    assert rpn_obj._stack.peek_x() == Decimal(6)

    # % operation
    rpn_obj._stack.push(Decimal(50))
    rpn_obj.btn_operation_two_arg('%')
    assert rpn_obj._stack.peek_x() == Decimal(3)

    # y square x operation
    rpn_obj._stack.push(Decimal(6))
    rpn_obj.btn_operation_two_arg('y^x')
    rpn_obj._stack.push(Decimal(6))
    rpn_obj._shift = True
    rpn_obj.btn_operation_two_arg('y^x')
    assert rpn_obj._stack.peek_x() == Decimal(3)


def test_two_args_float_operations(qtbot):
    pyrpn_window = rpn.PyRpnWindow()
    rpn_obj = rpn.PyRpnEvaluate(pyrpn_window)

    # sum operation
    rpn_obj._stack.push(Decimal('6.25'))
    rpn_obj._stack.push(Decimal('3.50'))
    rpn_obj.btn_operation_two_arg('+')
    assert rpn_obj._stack.peek_x() == Decimal('9.75')

    # subtract operation
    rpn_obj._stack.push(Decimal('4.55'))
    rpn_obj.btn_operation_two_arg('-')
    assert rpn_obj._stack.peek_x() == Decimal('5.2')

    # multiply operation
    rpn_obj._stack.push(Decimal('3.4'))
    rpn_obj.btn_operation_two_arg('*')
    assert rpn_obj._stack.peek_x() == Decimal('17.68')

    # division operation
    rpn_obj._stack.push(Decimal('2.5'))
    rpn_obj.btn_operation_two_arg('/')
    assert rpn_obj._stack.peek_x() == Decimal('7.072')

    # y expoent x operation
    rpn_obj._stack.push(Decimal(2))
    rpn_obj.btn_operation_two_arg('y^x')
    assert rpn_obj._stack.peek_x() == Decimal('50.013184')

    # % operation
    rpn_obj._stack.push(Decimal(25))
    rpn_obj.btn_operation_two_arg('%')
    assert rpn_obj._stack.peek_x() == Decimal('12.503296')

    # y square x operation
    rpn_obj._stack.push(Decimal(6))
    rpn_obj.btn_operation_two_arg('y^x')
    rpn_obj._stack.push(Decimal(6))
    rpn_obj._shift = True
    rpn_obj.btn_operation_two_arg('y^x')
    assert rpn_obj._stack.peek_x() == Decimal('12.503296')


@pytest.mark.parametrize(
    ("mode", "value", "expected_mode", "expected_value"),
    [
        ("DEG", "180", "RAD", math.pi),
        ("RAD", str(math.pi), "GRAD", 200),
        ("GRAD", "200", "DEG", 180),
        ("DEG", "0", "RAD", 0),
    ],
)
def test_drg_converts_stack_value(qtbot, mode, value, expected_mode, expected_value):
    window = rpn.PyRpnWindow()
    qtbot.addWidget(window)
    model = rpn.PyRpnEvaluate(window)
    model._angle_mesurement = mode
    model._stack.push(Decimal(value))
    model._shift = True

    model.btn_drg()

    assert model._angle_mesurement == expected_mode
    x_value = model._stack.peek_x()
    assert x_value is not None
    assert float(x_value) == pytest.approx(expected_value)


def test_drg_preserves_decimal_precision(qtbot):
    window = rpn.PyRpnWindow()
    qtbot.addWidget(window)
    model = rpn.PyRpnEvaluate(window)
    model._stack.push(Decimal("1.4142135623730950488016887242097"))
    model._shift = True

    model.btn_drg()

    assert model._stack.peek_x() == Decimal("0.02468268298976870137231044994478")


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def model(qtbot):
    """A fresh model (calculator just opened: stack = [None])"""
    window = rpn.PyRpnWindow()
    qtbot.addWidget(window)
    return rpn.PyRpnEvaluate(window)


@pytest.fixture
def controller(qtbot):
    """Model + view wired by the controller, to test buttons and keys"""
    window = rpn.PyRpnWindow()
    qtbot.addWidget(window)
    return rpn.PyRpn(window, rpn.PyRpnEvaluate(window))


def set_stack(model, *values):
    """Replace the stack with the given values (last one is X), as after an operation"""
    model._stack.cls()
    for value in values:
        model._stack.push(None if value is None else Decimal(str(value)))
    model._new_x = True
    model._after_enter = False
    model._pending_point = False
    model.update_display()


def type_keys(model, keys):
    """Type each character of keys with the number buttons ('0'-'9' and ',')"""
    for key in keys:
        model.btn_number(key)


def x_of(model) -> Decimal:
    value = model._stack.peek_x()
    assert value is not None
    return value


def items(model):
    return list(model._stack.items())


def x_text(model):
    return model._view.x_display.text()


def error_text(model):
    return model._view.error_label.text()


# ---------------------------------------------------------------------------
# Stack
# ---------------------------------------------------------------------------


def test_stack_empty():
    stack = rpn.Stack()
    assert stack.is_empty()
    assert stack.size() == 0
    assert stack.pop() is None
    assert stack.peek_x() is None
    assert stack.peek_y() is None
    assert stack.peek_z() is None


def test_stack_push_peek_swap_cls():
    stack = rpn.Stack()
    for value in (1, 2, 3):
        stack.push(Decimal(value))

    assert stack.size() == 3
    assert (stack.peek_z(), stack.peek_y(), stack.peek_x()) == (1, 2, 3)
    assert str(stack) == str([Decimal(1), Decimal(2), Decimal(3)])

    stack.swap()
    assert (stack.peek_y(), stack.peek_x()) == (3, 2)

    assert stack.pop() == 2
    stack.cls()
    assert stack.is_empty()


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (Decimal("2.50"), "2.5"),
        (Decimal("3.000"), "3"),
        (Decimal("-0.125"), "-0.125"),
        (Decimal("1.123456789012345678901234567890129"), "1.12345678901234567890123456789013"),
    ],
)
def test_stack_to_stack_value(number, expected):
    assert str(rpn.Stack.to_stack_value(number)) == expected


# ---------------------------------------------------------------------------
# Digit entry
# ---------------------------------------------------------------------------


def test_initial_state(model):
    assert items(model) == [None]
    assert x_text(model) == "0"
    assert model._view.angle_label.text() == "DEG"
    assert model._view.stack_label.text() == "STACK: 1"


def test_type_integer(model):
    type_keys(model, "123")
    assert items(model) == [Decimal(123)]
    assert x_text(model) == "123"


def test_type_decimal(model):
    type_keys(model, "5,25")
    assert x_of(model) == Decimal("5.25")
    assert x_text(model) == "5,25"


def test_pending_point_is_shown(model):
    type_keys(model, "5,")
    assert x_of(model) == Decimal(5)
    assert model._pending_point
    assert x_text(model) == "5,"


def test_comma_first_starts_with_zero(model):
    type_keys(model, ",5")
    assert x_of(model) == Decimal("0.5")
    assert x_text(model) == "0,5"


def test_second_comma_is_ignored(model):
    type_keys(model, "1,2,3")
    assert x_of(model) == Decimal("1.23")


def test_zeros_after_comma(model):
    type_keys(model, "0,0001")
    assert x_of(model) == Decimal("0.0001")
    assert x_text(model) == "0,0001"


def test_trailing_zeros_after_comma_are_kept(model):
    type_keys(model, "1,10")
    assert x_text(model) == "1,10"


def test_leading_zeros_are_ignored(model):
    type_keys(model, "007")
    assert x_of(model) == Decimal(7)
    assert x_text(model) == "7"


def test_entry_limited_to_display_size(model):
    type_keys(model, "1" * (rpn.DISPLAY_SIZE + 3))
    assert x_of(model) == Decimal("1" * rpn.DISPLAY_SIZE)


def test_entry_limit_does_not_count_the_comma(model):
    type_keys(model, "1" * (rpn.DISPLAY_SIZE - 1) + ",23")
    assert x_of(model) == Decimal("1" * (rpn.DISPLAY_SIZE - 1) + ".2")


def test_typing_after_operation_starts_new_number(model):
    set_stack(model, 7)
    type_keys(model, "3")
    assert items(model) == [Decimal(7), Decimal(3)]


# ---------------------------------------------------------------------------
# ENTER, BACK, DROP, SWAP, SHIFT
# ---------------------------------------------------------------------------


def test_enter_duplicates_x_and_next_number_replaces_copy(model):
    type_keys(model, "12")
    model.btn_enter()
    assert items(model) == [Decimal(12), Decimal(12)]

    type_keys(model, "3")
    assert items(model) == [Decimal(12), Decimal(3)]
    assert model._view.y_display.text() == "12"


def test_enter_then_operation(model):
    type_keys(model, "12")
    model.btn_enter()
    type_keys(model, "3")
    model.btn_operation_two_arg("-")
    assert items(model) == [Decimal(9)]


def test_back_removes_last_digit(model):
    type_keys(model, "123")
    model.btn_back()
    assert x_of(model) == Decimal(12)


def test_back_removes_pending_point(model):
    type_keys(model, "5,")
    model.btn_back()
    assert x_of(model) == Decimal(5)
    assert not model._pending_point
    assert x_text(model) == "5"


def test_back_removes_last_decimal_and_keeps_point(model):
    type_keys(model, "5,2")
    model.btn_back()
    assert x_of(model) == Decimal(5)
    assert model._pending_point
    assert x_text(model) == "5,"


def test_back_to_empty(model):
    type_keys(model, "7")
    model.btn_back()
    assert items(model) == [None]
    assert x_text(model) == "0"


def test_comma_after_back_to_empty(model):
    type_keys(model, "7")
    model.btn_back()
    type_keys(model, ",5")
    assert items(model) == [Decimal("0.5")]


def test_back_on_negative_single_digit(model):
    set_stack(model, -7)
    model.btn_back()
    assert items(model) == [None]


def test_back_on_empty_does_nothing(model):
    model.btn_back()
    assert items(model) == [None]


def test_drop_removes_x(model):
    set_stack(model, 1, 2)
    model.btn_drop()
    assert items(model) == [Decimal(1)]


def test_drop_last_item_leaves_empty_entry(model):
    set_stack(model, 1)
    model.btn_drop()
    assert items(model) == [None]
    assert not model._new_x
    assert x_text(model) == "0"


def test_shift_drop_clears_stack(model):
    set_stack(model, 1, 2, 3)
    model.btn_shift()
    model.btn_drop()
    assert items(model) == [None]
    assert not model._shift


def test_swap(model):
    set_stack(model, 1, 2)
    model.btn_swap()
    assert items(model) == [Decimal(2), Decimal(1)]
    assert x_text(model) == "1"
    assert model._view.y_display.text() == "2"


def test_swap_without_y(model):
    set_stack(model, 1)
    model.btn_swap()
    assert items(model) == [Decimal(1)]
    assert model._view.y_display.text() == "--"


def test_shift_swap_opens_stack_modal(model, monkeypatch):
    opened = []
    monkeypatch.setattr(rpn.StackModal, "exec", lambda self: opened.append(self) or 0)
    set_stack(model, 1, 2)
    model.btn_shift()
    model.btn_swap()

    assert len(opened) == 1
    assert items(model) == [Decimal(1), Decimal(2)]
    assert not model._shift


def test_shift_toggles_label(model):
    model.btn_shift()
    assert model._shift
    assert model._view.shift_label.text() == "SHIFT"
    model.btn_shift()
    assert not model._shift
    assert model._view.shift_label.text() == ""


# ---------------------------------------------------------------------------
# Constants and paste
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("method", "constant"), [("btn_pi", math.pi), ("btn_e", math.e)])
def test_constants(model, method, constant):
    set_stack(model, 1)
    getattr(model, method)()
    assert float(x_of(model)) == pytest.approx(constant)
    assert model._stack.peek_y() == Decimal(1)
    assert model._new_x


@pytest.mark.parametrize("method", ["btn_pi", "btn_e"])
def test_constant_replaces_empty_x(model, method):
    getattr(model, method)()
    assert model._stack.size() == 1


@pytest.mark.parametrize("method", ["btn_pi", "btn_e"])
def test_constant_replaces_enter_copy(model, method):
    type_keys(model, "9")
    model.btn_enter()
    getattr(model, method)()
    assert model._stack.size() == 2
    assert model._stack.peek_y() == Decimal(9)


@pytest.mark.parametrize("method", ["btn_pi", "btn_e"])
def test_constant_keeps_typed_number_in_y(model, method):
    type_keys(model, "5")
    getattr(model, method)()
    assert model._stack.size() == 2
    assert model._stack.peek_y() == Decimal(5)


def test_constant_then_operation(model):
    model.btn_pi()
    type_keys(model, "2")
    model.btn_operation_two_arg("*")
    assert float(x_of(model)) == pytest.approx(2 * math.pi)


class FakeClipboard:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


@pytest.fixture
def clipboard(monkeypatch):
    """Call clipboard('text') to fake the system clipboard content"""

    def set_text(text):
        monkeypatch.setattr(rpn.qtw.QApplication, "clipboard", lambda: FakeClipboard(text))

    return set_text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("42", Decimal(42)),
        ("1.234,5", Decimal("1234.5")),
        ("-0,25", Decimal("-0.25")),
        ("  7,5 reais", Decimal("7.5")),
    ],
)
def test_paste_valid_number_replaces_empty_x(model, clipboard, text, expected):
    clipboard(text)
    model.btn_paste()
    assert items(model) == [expected]
    assert model._new_x


def test_paste_after_result_pushes_new_value(model, clipboard):
    set_stack(model, 9)
    clipboard("3")
    model.btn_paste()
    assert items(model) == [Decimal(9), Decimal(3)]


def test_paste_replaces_enter_copy(model, clipboard):
    type_keys(model, "9")
    model.btn_enter()
    clipboard("3")
    model.btn_paste()
    assert items(model) == [Decimal(9), Decimal(3)]


@pytest.mark.parametrize("text", ["", "abc", "1,2,3", "12a"])
def test_paste_invalid_shows_error(model, clipboard, text):
    clipboard(text)
    model.btn_paste()
    assert items(model) == [None]
    assert error_text(model) == "ERROR"
    assert x_text(model) == "0"


# ---------------------------------------------------------------------------
# One argument operations
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("operation", "shift", "value", "expected"),
    [
        ("+/-", False, 5, Decimal(-5)),
        ("+/-", False, -2.5, Decimal("2.5")),
        ("1/x", False, 4, Decimal("0.25")),
        ("1/x", True, 5, Decimal(120)),  # factorial
        ("sqrt", False, 16, Decimal(4)),
        ("sqrt", True, 3, Decimal(9)),  # x²
        ("log", False, 1000, Decimal(3)),
        ("log", True, 2, Decimal(100)),  # 10^x
        ("ln", False, 1, Decimal(0)),
    ],
)
def test_one_arg_exact(model, operation, shift, value, expected):
    set_stack(model, 1, value)
    model._shift = shift
    model.btn_operation_one_arg(operation)
    assert items(model) == [Decimal(1), expected]
    assert not model._shift
    assert model._new_x


@pytest.mark.parametrize(
    ("mode", "operation", "shift", "value", "expected"),
    [
        ("DEG", "sin", False, 30, 0.5),
        ("DEG", "cos", False, 60, 0.5),
        ("DEG", "tan", False, 45, 1),
        ("DEG", "sin", True, 0.5, 30),
        ("DEG", "cos", True, 0.5, 60),
        ("DEG", "tan", True, 1, 45),
        ("RAD", "sin", False, math.pi / 2, 1),
        ("RAD", "cos", False, math.pi, -1),
        ("RAD", "sin", True, 1, math.pi / 2),
        ("GRAD", "sin", False, 100, 1),
        ("GRAD", "cos", False, 200, -1),
        ("GRAD", "sin", True, 1, 100),
        ("DEG", "ln", True, 1, math.e),  # e^x
    ],
)
def test_one_arg_approx(model, mode, operation, shift, value, expected):
    model._angle_mesurement = mode
    set_stack(model, value)
    model._shift = shift
    model.btn_operation_one_arg(operation)
    assert float(x_of(model)) == pytest.approx(expected, abs=1e-12)
    assert not model._shift


@pytest.mark.parametrize(
    ("operation", "value"),
    [
        ("1/x", 0),  # division by zero
        ("tan", 90),
        ("log", -1),
        ("log", 0),
        ("ln", -1),
        ("unknown", 1),
    ],
)
def test_one_arg_errors_keep_stack(model, operation, value):
    set_stack(model, 7, value)
    model.btn_operation_one_arg(operation)
    assert error_text(model) == "ERROR"
    assert items(model) == [Decimal(7), Decimal(value)]
    assert x_text(model) == str(value)
    # like after ENTER: the next number replaces x
    assert not model._new_x
    assert model._after_enter


@pytest.mark.parametrize("value", ["2.5", -1])
def test_factorial_needs_non_negative_integer(model, value):
    set_stack(model, value)
    model._shift = True
    model.btn_operation_one_arg("1/x")
    assert error_text(model) == "ERROR"
    assert items(model) == [Decimal(str(value))]
    assert not model._shift


@pytest.mark.parametrize(("operation", "value"), [("sin", 2), ("cos", 2)])
def test_shift_is_released_after_one_arg_error(model, operation, value):
    set_stack(model, value)
    model.btn_shift()
    model.btn_operation_one_arg(operation)
    assert error_text(model) == "ERROR"
    assert not model._shift
    assert model._view.shift_label.text() == ""


def test_shift_is_released_after_two_arg_error(model):
    set_stack(model, 8, 0)
    model.btn_shift()
    model.btn_operation_two_arg("y^x")
    assert error_text(model) == "ERROR"
    assert not model._shift


def test_shift_stays_on_when_argument_is_missing(model):
    model.btn_shift()
    model.btn_operation_one_arg("1/x")
    assert model._shift


def test_one_arg_without_x(model):
    model.btn_operation_one_arg("+/-")
    assert items(model) == [None]
    assert x_text(model) == "--"


# ---------------------------------------------------------------------------
# Two argument operations (errors and missing arguments)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("operation", "y", "x"),
    [("/", 1, 0), ("mod", 1, 0), ("unknown", 1, 2)],
)
def test_two_arg_errors_keep_stack(model, operation, y, x):
    set_stack(model, 9, y, x)
    model.btn_operation_two_arg(operation)
    assert error_text(model) == "ERROR"
    assert items(model) == [Decimal(9), Decimal(y), Decimal(x)]
    assert x_text(model) == str(x)
    assert model._view.y_display.text() == str(y)


def test_error_is_cleared_by_next_action(model):
    set_stack(model, 5, 0)
    model.btn_operation_two_arg("/")
    model.btn_drop()
    assert error_text(model) == ""


def divide_by_zero(model):
    set_stack(model, 1, 0)
    model.btn_operation_two_arg("/")


def test_typing_after_error_replaces_x(model):
    divide_by_zero(model)
    type_keys(model, "5")
    assert items(model) == [Decimal(1), Decimal(5)]


def test_back_after_error_then_type(model):
    divide_by_zero(model)
    model.btn_back()
    assert items(model) == [Decimal(1), None]
    type_keys(model, "5")
    assert items(model) == [Decimal(1), Decimal(5)]


def test_retry_after_error(model):
    divide_by_zero(model)
    type_keys(model, "5")
    model.btn_operation_two_arg("/")
    assert items(model) == [Decimal("0.2")]


def test_typing_after_one_arg_error_replaces_x(model):
    set_stack(model, 7, 0)
    model.btn_operation_one_arg("1/x")
    type_keys(model, "4")
    assert items(model) == [Decimal(7), Decimal(4)]


def test_back_on_result_edits_it(model):
    set_stack(model, 9, 3)
    model.btn_operation_two_arg("+")
    model.btn_back()
    type_keys(model, "5")
    assert items(model) == [Decimal(15)]


def test_after_error_drop_and_retry(model):
    set_stack(model, 5, 0)
    model.btn_operation_two_arg("/")
    model.btn_drop()
    type_keys(model, "2")
    model.btn_operation_two_arg("/")
    assert items(model) == [Decimal("2.5")]


def test_two_arg_without_x(model):
    model.btn_operation_two_arg("+")
    assert items(model) == [None]
    assert x_text(model) == "--"


def test_two_arg_without_y(model):
    set_stack(model, 5)
    model.btn_operation_two_arg("+")
    assert items(model) == [Decimal(5)]
    assert model._view.y_display.text() == "--"


def test_two_arg_with_negative_numbers(model):
    set_stack(model, -3, "-1.5")
    model.btn_operation_two_arg("*")
    assert x_of(model) == Decimal("4.5")


# ---------------------------------------------------------------------------
# DRG without SHIFT and angle conversion
# ---------------------------------------------------------------------------


def test_drg_without_shift_only_changes_mode(model):
    set_stack(model, 180)
    for expected in ("RAD", "GRAD", "DEG"):
        model.btn_drg()
        assert model._angle_mesurement == expected
        assert model._view.angle_label.text() == expected
    assert items(model) == [Decimal(180)]


def test_drg_round_trip_shows_original_value(model):
    type_keys(model, "180")
    for expected in ("3,14159265359", "200", "180"):
        model.btn_shift()
        model.btn_drg()
        assert x_text(model) == expected
    assert model._angle_mesurement == "DEG"


def test_shift_drg_with_empty_x_only_changes_mode(model):
    model.btn_shift()
    model.btn_drg()
    assert items(model) == [None]
    assert model._angle_mesurement == "RAD"
    assert not model._shift
    assert model._view.shift_label.text() == ""


def test_typing_after_shift_drg_starts_new_number(model):
    type_keys(model, "180")
    model.btn_shift()
    model.btn_drg()
    type_keys(model, "2")
    assert model._stack.size() == 2
    y_value = model._stack.peek_y()
    assert y_value is not None
    assert float(y_value) == pytest.approx(math.pi)
    assert x_of(model) == Decimal(2)


@pytest.mark.parametrize(
    ("mode", "angle", "radians"),
    [("DEG", 180, math.pi), ("GRAD", 200, math.pi), ("RAD", 2, 2)],
)
def test_angle_conversion(model, mode, angle, radians):
    model._angle_mesurement = mode
    assert float(model.convert_to_radian(Decimal(angle))) == pytest.approx(radians)
    assert float(model.convert_from_radian(Decimal(radians))) == pytest.approx(angle)


# ---------------------------------------------------------------------------
# Display formatting
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("number", "pending_point", "expected"),
    [
        (None, False, ("0", "", "")),
        (Decimal(0), False, ("0", "", "")),
        (Decimal(1234567), False, ("1.234.567", "", "")),
        (Decimal("-1234.5"), False, ("-1.234,5", "", "")),
        (Decimal("0.25"), False, ("0,25", "", "")),
        (Decimal(5), True, ("5,", "", "")),
        (Decimal(999_999_999_999), False, ("999.999.999.999", "", "")),
        (Decimal(1_234_567_890_123), False, ("1,23456789012", "x10", "12")),
        (Decimal(-1_234_567_890_123), False, ("-1,2345678901", "x10", "12")),
        (Decimal("1E+20"), False, ("1", "x10", "20")),
        (Decimal("0.0000000000001"), False, ("1", "x10", "-13")),
        (Decimal("3.1415926535897932384626433832795"), False, ("3,14159265359", "", "")),
        (Decimal("199.99999999999999999999999999999982"), False, ("200", "", "")),
        (Decimal("0.49999999999999994448884876874217"), False, ("0,5", "", "")),
        (Decimal("1234.56789012345678"), False, ("1.234,56789012", "", "")),
        (Decimal("-2.66666666666666666"), False, ("-2,6666666667", "", "")),
        (Decimal("999999999999.6"), False, ("1", "x10", "12")),
        (Decimal("1.10"), False, ("1,10", "", "")),
    ],
)
def test_format_number_for_display(model, number, pending_point, expected):
    assert model.format_number_for_display(number, pending_point) == expected


def test_display_shows_x_y_z_and_stack_size(model):
    set_stack(model, 1, 2, 3, 4)
    view = model._view
    assert (view.z_display.text(), view.y_display.text(), view.x_display.text()) == ("2", "3", "4")
    assert view.stack_label.text() == "STACK: 4"


def test_display_shows_exponent_for_big_numbers(model):
    set_stack(model, "1E+20", "1E+30", "1E+40")
    view = model._view
    assert (view.x_10.text(), view.x_exp.text()) == ("x10", "40")
    assert (view.y_10.text(), view.y_exp.text()) == ("x10", "30")
    assert (view.z_10.text(), view.z_exp.text()) == ("x10", "20")


# ---------------------------------------------------------------------------
# Stack modal
# ---------------------------------------------------------------------------


def label_texts(dialog):
    return [label.text() for label in dialog.findChildren(rpn.qtw.QLabel)]


def test_stack_modal_empty(qtbot):
    dialog = rpn.StackModal(None, rpn.Stack())
    qtbot.addWidget(dialog)
    assert label_texts(dialog) == ["Empty"]


def test_stack_modal_lists_items(qtbot):
    stack = rpn.Stack()
    for value in (None, Decimal("1.5"), Decimal(2)):
        stack.push(value)
    dialog = rpn.StackModal(None, stack)
    qtbot.addWidget(dialog)

    texts = label_texts(dialog)
    assert len(texts) == 3
    assert texts[1].endswith("1.5")
    assert texts[2].endswith("2")


def test_stack_modal_limits_height_for_many_items(qtbot):
    stack = rpn.Stack()
    for value in range(11):
        stack.push(Decimal(value))
    dialog = rpn.StackModal(None, stack)
    qtbot.addWidget(dialog)
    assert dialog.height() == 250


# ---------------------------------------------------------------------------
# Controller: buttons and keyboard wired to the model
# ---------------------------------------------------------------------------


def test_buttons_full_calculation(controller):
    view, model = controller._view, controller._model
    for button in ("btn_one", "btn_two", "btn_enter", "btn_three", "btn_add"):
        getattr(view, button).click()
    assert items(model) == [Decimal(15)]


@pytest.mark.parametrize(
    ("button", "expected"),
    [
        ("btn_minus", Decimal(4)),
        ("btn_multiply", Decimal(12)),
        ("btn_divide", Decimal(3)),
        ("btn_percent", Decimal("0.12")),
        ("btn_y_exp_x", Decimal(36)),
        ("btn_mod", Decimal(0)),
    ],
)
def test_two_arg_buttons(controller, button, expected):
    set_stack(controller._model, 6, 2)
    getattr(controller._view, button).click()
    assert x_of(controller._model) == expected


@pytest.mark.parametrize(
    ("button", "expected"),
    [
        ("btn_change_sign", -100),
        ("btn_x_inv", 0.01),
        ("btn_sqrt", 10),
        ("btn_sin", math.sin(math.radians(100))),
        ("btn_cos", math.cos(math.radians(100))),
        ("btn_tan", math.tan(math.radians(100))),
        ("btn_log", 2),
        ("btn_ln", math.log(100)),
    ],
)
def test_one_arg_buttons(controller, button, expected):
    set_stack(controller._model, 1, 100)
    getattr(controller._view, button).click()
    assert controller._model._stack.size() == 2
    assert float(x_of(controller._model)) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("button", "digit"),
    [
        ("btn_zero", "0"), ("btn_one", "1"), ("btn_two", "2"), ("btn_three", "3"),
        ("btn_four", "4"), ("btn_five", "5"), ("btn_six", "6"), ("btn_seven", "7"),
        ("btn_eight", "8"), ("btn_nine", "9"),
    ],
)
def test_digit_buttons(controller, button, digit):
    controller._view.btn_nine.click()
    getattr(controller._view, button).click()
    assert x_of(controller._model) == Decimal("9" + digit)


def test_control_buttons(controller):
    view, model = controller._view, controller._model
    view.btn_one.click()
    view.btn_decimal.click()
    view.btn_five.click()
    assert x_of(model) == Decimal("1.5")
    view.btn_back.click()
    assert x_text(model) == "1,"
    view.btn_enter.click()
    view.btn_two.click()
    view.btn_swap.click()
    assert items(model) == [Decimal(2), Decimal(1)]
    view.btn_drop.click()
    assert items(model) == [Decimal(2)]
    view.btn_pi.click()
    view.btn_e.click()
    assert model._stack.size() == 3
    view.btn_drg.click()
    assert model._angle_mesurement == "RAD"
    view.btn_shift.click()
    assert model._shift


@pytest.mark.parametrize(
    ("key", "check"),
    [
        (rpn.qtc.Qt.Key.Key_Period, lambda m: m._pending_point),
        (rpn.qtc.Qt.Key.Key_Return, lambda m: m._stack.size() == 2),
        (rpn.qtc.Qt.Key.Key_Shift, lambda m: m._shift),
    ],
)
def test_keyboard_keys(controller, qtbot, key, check):
    model = controller._model
    type_keys(model, "1")
    qtbot.keyClick(controller._view, key)
    assert check(model)


def test_set_pt_br_locale_tries_next_name(monkeypatch):
    tried = []

    def fake_setlocale(category, name):
        tried.append(name)
        if name != "pt_BR.UTF-8":
            raise rpn.locale.Error

    monkeypatch.setattr(rpn.locale, "setlocale", fake_setlocale)
    rpn.set_pt_br_locale()
    assert tried == ["pt-BR", "pt_BR.UTF-8"]


def test_set_pt_br_locale_fails_clearly(monkeypatch):
    def fake_setlocale(category, name):
        raise rpn.locale.Error

    monkeypatch.setattr(rpn.locale, "setlocale", fake_setlocale)
    with pytest.raises(rpn.locale.Error, match="pt-BR locale not available"):
        rpn.set_pt_br_locale()


def test_load_fonts_registers_display_font(qtbot):
    rpn.load_fonts()
    assert "DSEG7 Classic" in rpn.qtg.QFontDatabase.families()


def test_other_keys_are_ignored(model):
    type_keys(model, "1")
    model.key_pressed(rpn.qtc.Qt.Key.Key_A)
    assert items(model) == [Decimal(1)]
