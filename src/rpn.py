"""
PyRPN is an RPN calculator built with Python and PyQt.

copyright by HGF777@2023

for any information send an email to

hgf777@gmail.com

"""

import locale
import math
import os
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, getcontext
from functools import partial

import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
from PyQt6 import uic

PT_BR_LOCALES = ("pt-BR", "pt_BR.UTF-8", "pt_BR.utf8", "Portuguese_Brazil.1252")
PT_BR_DECIMAL_SEPARATOR = ","
PT_BR_THOUSANDS_SEPARATOR = "."


def set_pt_br_locale() -> None:
    """Use the pt-BR number format (1.234,5); each OS names the locale differently"""
    for name in PT_BR_LOCALES:
        try:
            locale.setlocale(locale.LC_ALL, name)
            return
        except locale.Error:
            continue
    raise locale.Error(f"pt-BR locale not available (tried {', '.join(PT_BR_LOCALES)})")


set_pt_br_locale()
# Folder holding the ui/ and icons/ resources: the PyInstaller bundle folder when
# frozen, otherwise the project root (this file lives in src/)
basedir = getattr(
    sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
getcontext().prec = 64
DISPLAY_SIZE = 12
PT_BR_NUMBER = re.compile(r"[+-]?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?")


class Stack:
    """
    HGF Stack implementation for python
    using Decimal to hold values to avoid floating point precision issues.
    None means an empty entry (nothing typed yet) or a missing position.
    """

    _items: list[Decimal | None]

    def __init__(self) -> None:
        self._items = []

    def __str__(self) -> str:
        return str(self._items)

    def items(self):
        return self._items

    def push(self, value: Decimal | None) -> None:
        self._items.append(value)

    def pop(self) -> Decimal | None:
        if self._items:
            return self._items.pop()
        else:
            return None

    def peek_x(self) -> Decimal | None:
        if self._items:
            return self._items[-1]
        else:
            return None

    def peek_y(self) -> Decimal | None:
        if len(self._items) > 1:
            return self._items[-2]
        else:
            return None

    def peek_z(self) -> Decimal | None:
        if len(self._items) > 2:
            return self._items[-3]
        else:
            return None

    def is_empty(self) -> bool:
        return not self._items

    def size(self) -> int:
        return len(self._items)

    def swap(self) -> None:
        self._items[-1], self._items[-2] = self._items[-2], self._items[-1]

    def cls(self):
        self._items = []
        
    @staticmethod
    def to_stack_value(number: float | Decimal) -> Decimal:
        """Round a result to 32 decimal places and drop trailing zeros"""
        return Decimal(format(number, '.32f').rstrip('0').rstrip('.'))


class StackModal(qtw.QDialog):
    """Modal dialog to show all stack items

    Args:
        parent: Qt Widget who is the parent of the dialog
        stack: Stack object with the rpn calculator stack
    """

    def __init__(self, parent, stack):
        super().__init__(parent)
        self.setWindowTitle("STACK")
        self.setWindowIcon(qtg.QIcon(os.path.join(basedir, "icons", "stack.svg")))
        self.setModal(True)
        self.setFixedWidth(150)
        self.setStyleSheet("color: white")

        self.scroll_swap = qtw.QScrollArea(self)
        self.scroll_swap.setWidgetResizable(True)
        self.scroll_swap.setHorizontalScrollBarPolicy(
            qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_content = qtw.QWidget(self.scroll_swap)
        self.scroll_swap.setWidget(self.scroll_content)

        self.layout_swap = qtw.QVBoxLayout(self)
        self.layout_swap.addWidget(self.scroll_swap)

        self.scroll_layout = qtw.QVBoxLayout(self.scroll_content)

        if stack.is_empty():
            self.scroll_layout.addWidget(qtw.QLabel("Empty"))
        else:
            if stack.size() > 10:
                self.setFixedHeight(250)
            for idx, number in enumerate(stack.items(), 1):
                shown = "" if number is None else format(number, "f")
                self.scroll_layout.addWidget(
                    qtw.QLabel(f'<font color="#8AF">{idx}:</font> {shown}')
                )


class PyRpnWindow(qtw.QMainWindow):
    """PyRPN's view class -  main window (GUI)

    description:
        Loads a UI file
    """
    
    x_display: qtw.QLineEdit
    x_10: qtw.QLineEdit
    x_exp: qtw.QLineEdit
    y_display: qtw.QLineEdit
    y_10: qtw.QLineEdit
    y_exp: qtw.QLineEdit
    z_display: qtw.QLineEdit
    z_10: qtw.QLineEdit
    z_exp: qtw.QLineEdit
    shift_label: qtw.QLabel
    error_label: qtw.QLabel
    angle_label: qtw.QLabel
    stack_label: qtw.QLabel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(os.path.join(basedir, "ui", "calculator.ui"), self)  # type: ignore
        self.setWindowIcon(qtg.QIcon(os.path.join(basedir, "icons", "calc.svg")))
        # Paste has no button in the UI file, so the view creates its shortcut
        self.shortcut_paste = qtg.QShortcut(qtg.QKeySequence.StandardKey.Paste, self)

    key_signal = qtc.pyqtSignal(int)

    def keyPressEvent(self, a0):
        self.key_signal.emit(a0.key())


class PyRpnEvaluate:
    """PyRPN's model class

    args:
        view: View object -> PyRpnWindow
    """

    def __init__(self, view: PyRpnWindow):
        self._view: PyRpnWindow = view
        self._stack: Stack = Stack()
        self._stack.push(None)
        self._after_enter: bool = True
        self._new_x: bool = False
        # True right after the decimal point key, before any decimal digit is typed
        # (a Decimal can't hold a trailing point, so x shows "5," while it holds 5)
        self._pending_point: bool = False
        self._shift: bool = False
        self._angle_mesurement: str = "DEG"
        self.update_display()

    def update_display(self):
        """Draws stack and other information in the display area"""
        self._view.error_label.setText("")

        print(f"update new_x: {self._new_x} - after_enter: {self._after_enter}")
        print(f"update stack: {self._stack.items()}")
        if self._stack.peek_x() is not None:
            text, base, exp = self.format_number_for_display(
                self._stack.peek_x(), self._pending_point
            )
            self._view.x_display.setText(text)
            self._view.x_10.setText(base)
            self._view.x_exp.setText(exp)
        else:
            self._view.x_display.setText("0")
            self._view.x_10.setText("")
            self._view.x_exp.setText("")
            
        if self._stack.peek_y() is not None:
            text, base, exp = self.format_number_for_display(self._stack.peek_y())
            self._view.y_display.setText(text)
            self._view.y_10.setText(base)
            self._view.y_exp.setText(exp)
        else:
            self._view.y_display.setText("")
            self._view.y_10.setText("")
            self._view.y_exp.setText("")

        if self._stack.peek_z() is not None:
            text, base, exp = self.format_number_for_display(self._stack.peek_z())
            self._view.z_display.setText(text)
            self._view.z_10.setText(base)
            self._view.z_exp.setText(exp)
        else:
            self._view.z_display.setText("")
            self._view.z_10.setText("")
            self._view.z_exp.setText("")

        self._view.angle_label.setText(self._angle_mesurement)
        self._view.stack_label.setText(f"STACK: {self._stack.size()}")
        
    def number_overflow_display(self, number: str):
        max_lenght = DISPLAY_SIZE + (1 if '.' in number else 0)
        return len(number) > max_lenght
    
    def format_overflow_number(self, number: str) -> tuple[str, str, str]:
        """Format a number string that exceeds the display size."""
        negative = number.startswith("-")
        # DISPLAY_SIZE chars available: the sign and the decimal point take one each
        decimals = DISPLAY_SIZE - 1 - (1 if negative else 0)

        mantissa, exponent = format(Decimal(number), f".{decimals}e").split("e")
        integer, _, decimal = mantissa.partition(".")
        decimal = decimal.rstrip("0")

        formatted = self.format_integer_part(integer)
        if decimal:
            formatted += PT_BR_DECIMAL_SEPARATOR + decimal

        return (formatted, "x10", str(int(exponent)))

    def round_to_display(self, number: Decimal) -> str | None:
        """Round number to the decimals that fit in the display, dropping the
        trailing zeros. None if it can't be shown without scientific notation
        (integer part too big, or it would round to zero)
        """
        integer_digits = len(format(abs(number), "f").partition(".")[0])
        decimals = DISPLAY_SIZE - integer_digits - (1 if number < 0 else 0)
        if decimals < 0:
            return None
        rounded = number.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
        text = format(rounded, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        if rounded == 0 or self.number_overflow_display(text):
            return None
        return text

    def format_integer_part(self, integer: str) -> str:
        """Format the integer part using Brazilian thousands separators."""
        return f"{int(integer):,d}".replace(",", PT_BR_THOUSANDS_SEPARATOR)

    def format_number_for_display(
        self, number: Decimal | None, pending_point: bool = False
    ) -> tuple[str, str, str]:
        """Format a stack value according to locale settings with proper grouping.

        Args:
            number (Decimal | None): the stack value, None for an empty entry
            pending_point (bool): True if the decimal point was typed but no decimal
                                digit yet, so the display must show "5," for 5

        Returns:
            tuple[str, str, str]: (number, '', '') or, when it doesn't fit the
                display, (mantissa, 'x10', exponent)
        """
        if number is None:
            return ("0", "", "")

        text = format(number, "f")
        if self.number_overflow_display(text):
            # too many digits: round the decimals to fit the display, the stack
            # keeps the full precision
            rounded = self.round_to_display(number)
            if rounded is None:
                return self.format_overflow_number(text)
            text = rounded

        sign = "-" if text.startswith("-") else ""
        integer, _, decimal = text.lstrip("-").partition(".")
        formatted = sign + self.format_integer_part(integer)
        if decimal or pending_point:
            formatted += PT_BR_DECIMAL_SEPARATOR + decimal

        return (formatted, "", "")

    def _entry_text(self, value: Decimal | None) -> str:
        """Text of the number being typed, including a pending decimal point"""
        if value is None:
            return ""
        return format(value, "f") + ("." if self._pending_point else "")

    def no_arg(self, arg):
        """Shows '--' if the stack is empty for a given argument

        Args:
            arg (str): x or y
        """
        if arg == "x":
            self._view.x_display.setText("--")
        else:
            self._view.y_display.setText("--")

    def key_pressed(self, key):
        """Capture aditional keys used in the calculator not directly associated with the buttons

        Args:
            key (Qt.Key): Key code pressed
        """
        match key:
            case qtc.Qt.Key.Key_Period:
                self.btn_number(",")
            case qtc.Qt.Key.Key_Return:
                self.btn_enter()
            case qtc.Qt.Key.Key_Shift:
                self.btn_shift()

    def btn_number(self, key):
        """Function for all numbers and decimal point(comma) buttons
            Insert a digit in the stack last entrie

        Args:
            key (str): one of these caracters -> '0123456789,.'
        """
        if self._new_x:
            self._stack.push(None)
            self._pending_point = False
            self.update_display()
            self._new_x = False
            self._after_enter = True
        x_value = self._stack.peek_x()
        text = self._entry_text(x_value)
        max_length = DISPLAY_SIZE + (1 if "." in text else 0)
        if x_value is None or self._after_enter or len(text) < max_length:
            self._add_digit(key)

    def _add_digit(self, key):
        """Function to enter a new digit to the number in the last stack entry

        Args:
            key (str): one of these characters -> '0123456789,.'
        """
        if self._after_enter:
            self._stack.pop()
            self._after_enter = False
            if key == ",":
                self._stack.push(Decimal(0))
                self._pending_point = True
            else:
                self._stack.push(Decimal(key))
                self._pending_point = False
        else:
            x_value = self._stack.pop()
            text = self._entry_text(x_value)
            if key == ",":
                if "." not in text:
                    self._pending_point = True
                    if x_value is None:
                        x_value = Decimal(0)
            elif not (key == "0" and text in ("0", "-0")):
                self._pending_point = False
                x_value = Decimal(text + key)
            self._stack.push(x_value)

        self.update_display()

    def convert_to_radian(self, angle: Decimal) -> Decimal:
        """Convert an angle from Degrees or Gradians to Radians

        Args:
            angle (Decimal): angle in degree or gradian

        Returns:
            Decimal: angle in radian
        """
        response: float = float(angle)
        
        if self._angle_mesurement == "DEG":
            response = math.radians(angle)
        elif self._angle_mesurement == "GRAD":
            angle = angle * 360 / 400
            response = math.radians(angle)
        return Decimal(response)

    def convert_from_radian(self, angle: Decimal) -> Decimal:
        """Convert an angle from Radians to Degrees or Gradians

        Args:
            angle (Decimal): angle in radian

        Returns:
            Decimal: angle in degree or gradian
        """
        response: float = float(angle)
        
        if self._angle_mesurement == "DEG":
            response = math.degrees(angle)
        elif self._angle_mesurement == "GRAD":
            response = math.degrees(angle)
            response = response * 400 / 360
        return Decimal(response)

    def btn_operation_one_arg(self, operation):
        """Function to connect all one argument buttons

        Args:
            operation (str): one arg button label -> +/-, 1/x, sqrt, sin, cos, tan, log, ln
        """
        result: Decimal = Decimal(0)
        x_value = self._stack.peek_x()
        if x_value is not None:
            # SHIFT is used by this operation even if it fails
            shift = self._shift
            if shift:
                self.btn_shift()
            self._stack.pop()
            self._pending_point = False
            _error = False
            try:
                match operation:
                    case "+/-":
                        result = -x_value
                    case "1/x":
                        if shift:
                            # factorial only for integers (2.5 is an error, not 2!)
                            if x_value != x_value.to_integral_value():
                                _error = True
                            else:
                                result = Decimal(math.factorial(int(x_value)))
                        else:
                            result = 1 / x_value
                    case "sqrt":
                        if shift:
                            result = x_value ** Decimal(2)
                        else:
                            result = x_value ** Decimal("0.5")
                    case "sin":
                        if shift:
                            result = Decimal(math.asin(x_value))
                            result = self.convert_from_radian(result)
                        else:
                            angle = self.convert_to_radian(x_value)
                            result = Decimal(math.sin(angle))
                    case "cos":
                        if shift:
                            result = Decimal(math.acos(x_value))
                            result = self.convert_from_radian(result)
                        else:
                            angle = self.convert_to_radian(x_value)
                            result = Decimal(math.cos(angle))
                    case "tan":
                        if shift:
                            result = Decimal(math.atan(x_value))
                            result = self.convert_from_radian(result)
                        else:
                            angle = self.convert_to_radian(x_value)
                            if angle % Decimal(math.pi / 2) != 0:
                                result = Decimal(math.tan(angle))
                            else:
                                _error = True
                    case "log":
                        if shift:
                            result = 10 ** x_value
                        else:
                            result = Decimal(math.log10(x_value))
                    case "ln":
                        if shift:
                            result = Decimal(math.e) ** x_value
                        else:
                            result = Decimal(math.log(x_value))
                    case _:
                        _error = True
            except Exception:  # noqa: BLE001
                _error = True
            if not _error:
                self._stack.push(Stack.to_stack_value(result))
                self._new_x = True
                self.update_display()
            else:
                # an error doesn't change the stack: x goes back so it can be fixed,
                # and like after ENTER the next number replaces it
                self._stack.push(x_value)
                self._new_x = False
                self._after_enter = True
                self.update_display()
                self.error()
        else:
            self.no_arg("x")

    def btn_operation_two_arg(self, operation: str) -> None:
        """Function to connect all two arguments buttons and calculates the operation 
        from the two arguments provided on the stack.

        Args:
            operation (str): two args button label -> +, -, *, /, %, y^x, mod
        """
        _error: bool = False
        result: Decimal = Decimal(0)

        x_value = self._stack.peek_x()
        y_value = self._stack.peek_y()
        if x_value is None:
            self.no_arg("x")
        elif y_value is not None:
            # SHIFT is used by this operation even if it fails
            shift = self._shift
            if shift:
                self.btn_shift()
            self._stack.pop()
            self._stack.pop()
            self._pending_point = False
            try:
                match operation:
                    case "+":
                        result = y_value + x_value
                    case "-":
                        result = y_value - x_value
                    case "*":
                        result = y_value * x_value
                    case "/":
                        result = y_value / x_value
                    case "%":
                        result = y_value * (x_value / 100)
                    case "y^x":
                        if shift:
                            result = y_value ** (Decimal(1) / x_value)
                        else:
                            result = y_value ** x_value
                    case "mod":
                        result = y_value % x_value
                    case _:
                        _error = True
            except Exception:  # noqa: BLE001   
                _error = True
            if not _error:
                # result = round(result, 16)
                stack_result: Decimal = Stack.to_stack_value(result)
                self._stack.push(stack_result)
                self.update_display()
            else:
                # an error doesn't change the stack: y and x go back,
                # and like after ENTER the next number replaces x
                self._stack.push(y_value)
                self._stack.push(x_value)
                self._new_x = False
                self._after_enter = True
                self.update_display()
                self.error()
                return
        else:
            self.no_arg("y")
        self._new_x = True

    def btn_drop(self):
        """Function to connect the DROP button
        Remove the last entrie from the stack
        """
        if self._shift:
            self._stack.cls()
            self.btn_shift()
        else:
            self._stack.pop()
            self._new_x = True
        self._pending_point = False
        if self._stack.is_empty():
            self._stack.push(None)
            self._new_x = False
        self.update_display()

    def btn_swap(self):
        """Function to connect the SWAP button
        Invert the position of the two last entries in the stack
        """
        if self._shift:
            stack_modal = StackModal(parent=self._view, stack=self._stack)
            stack_modal.exec()
            self.btn_shift()
        else:
            if self._stack.peek_y() is not None:
                self._pending_point = False
                self._stack.swap()
                self.update_display()
            else:
                self.no_arg("y")
            # self._new_x = True

    def btn_enter(self):
        """Function to connect the ENTER buttton
        Enter a number to the stack, duplicates it and waits for a new number
        """
        self._stack.push(self._stack.peek_x())
        self._pending_point = False
        self.update_display()
        self._after_enter = True

    def btn_back(self):
        """Function to connect the BACKSPACE button
        Remove the last character from the last entry in the stack,
        x becomes a number being typed (next digits continue it)
        """
        x_value = self._stack.peek_x()
        if x_value is not None:
            text = self._entry_text(x_value)[:-1]
            self._pending_point = text.endswith(".")
            text = text.removesuffix(".")
            self._stack.pop()
            self._stack.push(None if text in ("", "-") else Decimal(text))
            self._new_x = False
            self._after_enter = False
            self.update_display()

    def btn_shift(self):
        """Function to connect the SHIFT button
        Toggle (on/off) the shift button
        """
        self._shift = not self._shift

        if self._shift:
            self._view.shift_label.setText("SHIFT")
        else:
            self._view.shift_label.setText("")

    def _push_constant(self, value: float) -> None:
        """Put a constant in x: it replaces an empty x or the copy left by ENTER,
        otherwise it is pushed over x (a typed number or a result stays in y)
        """
        if not self._new_x and (self._after_enter or self._stack.peek_x() is None):
            self._stack.pop()
        self._stack.push(Stack.to_stack_value(value))
        self._pending_point = False
        self._after_enter = False
        self._new_x = True
        self.update_display()

    def btn_pi(self):
        """Function to connect the PI button
        Insert the pi number in the stack
        """
        self._push_constant(math.pi)

    def btn_e(self):
        """Function to connect the E button
        Insert the e number in the stack
        """
        self._push_constant(math.e)

    def btn_paste(self):
        """Function to connect the paste shortcut (Ctrl+V)
        Put the first number in the clipboard text (pt-BR format) in x,
        or show ERROR if the text doesn't start with a valid number
        """
        clipboard = qtw.QApplication.clipboard()
        words = clipboard.text().split() if clipboard else []
        if not words or not PT_BR_NUMBER.fullmatch(words[0]):
            self.error()
            return

        value = Decimal(words[0].replace(".", "").replace(",", "."))
        if not self._new_x:
            # x is empty, a copy left by ENTER or a number being typed: replace it
            self._stack.pop()
        self._stack.push(value)
        self._pending_point = False
        self._after_enter = False
        self._new_x = True
        self.update_display()

    def btn_drg(self):
        """Function to connect the DRG button
        Change or convert degrees units (DEG/GRAD/RAD)
        """
        response: Decimal = Decimal(0)
        pi = Decimal(
            "3.1415926535897932384626433832795028841971693993751058209749445923"
        )

        self._pending_point = False
        x_value = None
        if self._shift:
            # SHIFT DRG converts x; with an empty x it only changes the unit
            self.btn_shift()
            if self._stack.peek_x() is not None:
                x_value = self._stack.pop()
        match self._angle_mesurement:
            case "DEG":
                self._angle_mesurement = "RAD"
                if x_value is not None:
                    response = x_value * pi / Decimal(180)
            case "RAD":
                self._angle_mesurement = "GRAD"
                if x_value is not None:
                    response = x_value * Decimal(200) / pi
            case _:
                self._angle_mesurement = "DEG"
                if x_value is not None:
                    response = x_value * Decimal(9) / Decimal(10)

        if x_value is not None:
            self._stack.push(Stack.to_stack_value(response))
            self._new_x = True
        self.update_display()

    def error(self):
        """Show 'ERROR' in the error label, x keeps showing its value"""
        self._view.error_label.setText("ERROR")


class PyRpn:
    """PyRPN's controller class

    description:
        connects all QT signals send from the view to functions in the model
    """

    def __init__(self, view, model):
        self._view = view
        self._model = model
        self._connectSignalsAndSlots()

    def _connectSignalsAndSlots(self):
        """Connect all buttons with QT signals"""
        # Keyboard keys not directly shown in the calculator
        self._view.key_signal.connect(
            self._model.key_pressed
        )  # using personalized signal key_signal

        # Paste shortcut (Ctrl+V), no button in the UI
        self._view.shortcut_paste.activated.connect(self._model.btn_paste)

        # Numbers buttons
        self._view.btn_zero.clicked.connect(partial(self._model.btn_number, "0"))
        self._view.btn_one.clicked.connect(partial(self._model.btn_number, "1"))
        self._view.btn_two.clicked.connect(partial(self._model.btn_number, "2"))
        self._view.btn_three.clicked.connect(partial(self._model.btn_number, "3"))
        self._view.btn_four.clicked.connect(partial(self._model.btn_number, "4"))
        self._view.btn_five.clicked.connect(partial(self._model.btn_number, "5"))
        self._view.btn_six.clicked.connect(partial(self._model.btn_number, "6"))
        self._view.btn_seven.clicked.connect(partial(self._model.btn_number, "7"))
        self._view.btn_eight.clicked.connect(partial(self._model.btn_number, "8"))
        self._view.btn_nine.clicked.connect(partial(self._model.btn_number, "9"))
        self._view.btn_decimal.clicked.connect(partial(self._model.btn_number, ","))

        # Control buttons
        self._view.btn_drop.clicked.connect(self._model.btn_drop)
        self._view.btn_swap.clicked.connect(self._model.btn_swap)
        self._view.btn_enter.clicked.connect(self._model.btn_enter)
        self._view.btn_back.clicked.connect(self._model.btn_back)
        self._view.btn_shift.clicked.connect(self._model.btn_shift)
        self._view.btn_pi.clicked.connect(self._model.btn_pi)
        self._view.btn_e.clicked.connect(self._model.btn_e)
        self._view.btn_drg.clicked.connect(self._model.btn_drg)

        # Two args operation buttons
        self._view.btn_add.clicked.connect(
            partial(self._model.btn_operation_two_arg, "+")
        )
        self._view.btn_minus.clicked.connect(
            partial(self._model.btn_operation_two_arg, "-")
        )
        self._view.btn_multiply.clicked.connect(
            partial(self._model.btn_operation_two_arg, "*")
        )
        self._view.btn_divide.clicked.connect(
            partial(self._model.btn_operation_two_arg, "/")
        )
        self._view.btn_percent.clicked.connect(
            partial(self._model.btn_operation_two_arg, "%")
        )
        self._view.btn_y_exp_x.clicked.connect(
            partial(self._model.btn_operation_two_arg, "y^x")
        )
        self._view.btn_mod.clicked.connect(
            partial(self._model.btn_operation_two_arg, "mod")
        )

        # One arg operation buttons
        self._view.btn_change_sign.clicked.connect(
            partial(self._model.btn_operation_one_arg, "+/-")
        )
        self._view.btn_x_inv.clicked.connect(
            partial(self._model.btn_operation_one_arg, "1/x")
        )
        self._view.btn_sqrt.clicked.connect(
            partial(self._model.btn_operation_one_arg, "sqrt")
        )
        self._view.btn_sin.clicked.connect(
            partial(self._model.btn_operation_one_arg, "sin")
        )
        self._view.btn_cos.clicked.connect(
            partial(self._model.btn_operation_one_arg, "cos")
        )
        self._view.btn_tan.clicked.connect(
            partial(self._model.btn_operation_one_arg, "tan")
        )
        self._view.btn_log.clicked.connect(
            partial(self._model.btn_operation_one_arg, "log")
        )
        self._view.btn_ln.clicked.connect(
            partial(self._model.btn_operation_one_arg, "ln")
        )


def load_fonts():
    """Register the fonts in fonts/ so the app doesn't depend on installed fonts"""
    fonts_dir = os.path.join(basedir, "fonts")
    for name in os.listdir(fonts_dir):
        if name.lower().endswith(".ttf"):
            qtg.QFontDatabase.addApplicationFont(os.path.join(fonts_dir, name))


def main():
    """PyRPN's main function"""
    pyrpn_app = qtw.QApplication([])
    load_fonts()
    pyrpn_window = PyRpnWindow()
    pyrpn_window.show()
    PyRpn(pyrpn_window, PyRpnEvaluate(pyrpn_window))
    sys.exit(pyrpn_app.exec())


if __name__ == "__main__":
    main()
