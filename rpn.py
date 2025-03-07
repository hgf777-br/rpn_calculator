"""
PyRPN is an RPN calculator built with Python and PyQt.

copyright by HGF777@2023

for any information send an email to

hgf777@gmail.com

"""

import os
import sys
import locale
import math
from functools import partial

import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
from PyQt6 import uic

locale.setlocale(locale.LC_ALL, ('pt-BR', ''))
basedir = os.path.dirname(__file__)


class Stack:
    """HGF Stack implementation for python"""

    def __init__(self) -> None:
        self._items = []

    def __str__(self) -> str:
        return str(self._items)

    def items(self):
        return self._items

    def push(self, value) -> None:
        self._items.append(value)

    def pop(self) -> str:
        if self._items:
            return self._items.pop()
        else:
            return ''

    def peek_x(self) -> str | None:
        if self._items:
            return self._items[-1]
        else:
            return None

    def peek_y(self) -> str | None:
        if len(self._items) > 1:
            return self._items[-2]
        else:
            return None

    def peek_z(self) -> str | None:
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


class StackModal(qtw.QDialog):
    """Modal dialog to show all stack items

    Args:
        parent: Qt Widget who is the parent of the dialog
        stack: Stack object with the rpn calculator stack
    """

    def __init__(self, parent, stack):
        super().__init__(parent)
        self.setWindowTitle("STACK")
        self.setWindowIcon(qtg.QIcon(os.path.join(basedir, './icons/stack.svg')))
        self.setModal(True)
        self.setFixedWidth(150)
        self.setStyleSheet('color: white')

        self.scroll = qtw.QScrollArea(self)  # type: ignore
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_content = qtw.QWidget(self.scroll)
        self.scroll.setWidget(self.scroll_content)

        self.layout = qtw.QVBoxLayout(self)  # type: ignore
        self.layout.addWidget(self.scroll)

        self.scroll_layout = qtw.QVBoxLayout(self.scroll_content)  # type: ignore

        if stack.is_eempty():
            self.scroll_layout.addWidget(qtw.QLabel('Empty'))
        else:
            if stack.size() > 10:
                self.setFixedHeight(250)
            for idx, number in enumerate(stack.items(), 1):
                self.scroll_layout.addWidget(qtw.QLabel(f'<font color="#8AF">{idx}:</font> {number}'))


class PyRpnWindow(qtw.QMainWindow):
    """PyRPN's view class -  main window (GUI)

    description:
        Loads a UI file
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(os.path.join(basedir, './ui/calculator.ui'), self)  # type: ignore
        self.setWindowIcon(qtg.QIcon(os.path.join(basedir, './icons/calc.svg')))

    key_signal = qtc.pyqtSignal(int)

    def keyPressEvent(self, event):
        self.key_signal.emit(event.key())


class PyRpnEvaluate:
    """PyRPN's model class

    args:
        view: View object -> PyRpnWindow
    """

    def __init__(self, view):
        self._view = view
        self._stack = Stack()
        self._stack.push('0')
        self._after_enter = True
        self._new_x = False
        self._shift = False
        self._angle_mesurement = 'DEG'
        self.update_display()

    def update_display(self):
        """Draws stack and other information in the display area"""

        print('update ->', self._stack)
        self._view.x_display.setText(self._stack.peek_x())
        if self._stack.peek_y():
            self._view.y_display.setText(self._stack.peek_y())
        else:
            self._view.y_display.setText('')
        if self._stack.peek_z():
            self._view.z_display.setText(self._stack.peek_z())
        else:
            self._view.z_display.setText('')
        self._view.angle_label.setText(self._angle_mesurement)
        self._view.stack_label.setText(f'STACK: {self._stack.size()}')

    def no_arg(self, arg):
        """Shows '--' if the stack is empty for a given argument

        Args:
            arg (str): x or y
        """
        if arg == 'x':
            self._view.x_display.setText('--')
        else:
            self._view.y_display.setText('--')

    def key_pressed(self, key):
        """Capture aditional keys used in the calculator not directly associated with the buttons

        Args:
            key (Qt.Key): Key code pressed
        """
        match key:
            case qtc.Qt.Key.Key_Period:
                self.btn_number(',')
            case qtc.Qt.Key.Key_Return:
                self.btn_enter()
            case qtc.Qt.Key.Key_Shift:
                self.btn_shift()

    def btn_number(self, key):
        """Function for all numbers and decimal point(comma) buttons
            Insert a digit in the stack last entrie

        Args:
            key (str): one of these caracters -> '0123456789,'
        """
        if self._new_x:
            self._stack.push('')
            self.update_display()
            self._new_x = False
            self._after_enter = True
        x_value = self._stack.peek_x()
        if not x_value or self._after_enter:
            if key in '0123456789,':
                self._add_digit(key)
        elif len(x_value.replace('.', '').replace(',', '')) < 12:
            self._add_digit(key)

    def _add_digit(self, key):
        """Function to enter a new digit to the number in the stack last entrie

        Args:
            key (str): one of these caracters -> '0123456789,'
        """
        if not self._stack.peek_x() or self._after_enter:
            if self._after_enter:
                self._stack.pop()
                self._after_enter = False
            if key == ',':
                self._stack.push('0,')
            else:
                self._stack.push(key)
        else:
            x_value = self._stack.pop()
            if key in '0123456789':
                if ',' in x_value:  # type: ignore
                    x_value += key
                else:
                    x_value = x_value.replace('.', '') + key  # type: ignore
                    for i in range(len(x_value)):
                        if i != 0 and not i % 3:
                            x_value = x_value[: -i - (i // 3 - 1)] + '.' + x_value[-i - (i // 3 - 1):]
                x_value = self.format_number(x_value)
            elif key == ',' and ',' not in x_value:  # type: ignore
                x_value += key
            self._stack.push(x_value)

        self.update_display()

    def convert_to_radian(self, angle):
        """Convert an angle from Degrees or Gradians to Radians

        Args:
            angle (float): angle in degree or gradian

        Returns:
            float: angle in radian
        """
        if self._angle_mesurement == 'DEG':
            angle = math.radians(angle)
        elif self._angle_mesurement == 'GRAD':
            angle = angle * 360 / 400
            angle = math.radians(angle)
        return angle

    def convert_from_radian(self, angle):
        """Convert an angle from Radians to Degrees or Gradians

        Args:
            angle (float): angle in radian

        Returns:
            float: angle in degree or gradian
        """
        if self._angle_mesurement == 'DEG':
            angle = math.degrees(angle)
        elif self._angle_mesurement == 'GRAD':
            angle = math.degrees(angle)
            angle = angle * 400 / 360
        return angle

    def btn_operation_one_arg(self, operation):
        """Function to connect all one argument buttons

        Args:
            operation (str): one arg button label -> +/-, 1/x, sqrt, sin, cos, tan, log, ln
        """
        result = 0
        x_value = ''
        if self._stack.peek_x():
            x_value = self._stack.pop()
            _error = False
            try:
                match operation:
                    case '+/-':
                        result = locale.atof(x_value) * -1.0
                    case '1/x':
                        if self._shift:
                            result = math.factorial(locale.atoi(x_value))
                            self.btn_shift()
                        else:
                            result = 1 / locale.atof(x_value)
                    case 'sqrt':
                        if self._shift:
                            result = locale.atof(x_value) ** 2.0
                            self.btn_shift()
                        else:
                            result = locale.atof(x_value) ** 0.5
                    case 'sin':
                        if self._shift:
                            result = math.asin(locale.atof(x_value))
                            result = self.convert_from_radian(result)
                            self.btn_shift()
                        else:
                            angle = self.convert_to_radian(locale.atof(x_value))
                            result = math.sin(angle)
                    case 'cos':
                        if self._shift:
                            result = math.acos(locale.atof(x_value))
                            result = self.convert_from_radian(result)
                            self.btn_shift()
                        else:
                            angle = self.convert_to_radian(locale.atof(x_value))
                            result = math.cos(angle)
                    case 'tan':
                        if self._shift:
                            result = math.atan(locale.atof(x_value))
                            result = self.convert_from_radian(result)
                            self.btn_shift()
                        else:
                            angle = self.convert_to_radian(locale.atof(x_value))
                            if angle % (math.pi / 2) != 0:
                                result = math.tan(angle)
                            else:
                                _error = True
                    case 'log':
                        if self._shift:
                            result = 10 ** locale.atof(x_value)
                            self.btn_shift()
                        else:
                            result = math.log10(locale.atof(x_value))
                    case 'ln':
                        if self._shift:
                            result = math.e ** locale.atof(x_value)
                            self.btn_shift()
                        else:
                            result = math.log(locale.atof(x_value))
                    case _:
                        _error = True
            except Exception:
                _error = True
            if not _error:
                if result > 999999999999.0:
                    result = locale.format_string('%.8e', result, grouping=True)
                else:
                    result = locale.format_string('%.12g', result, grouping=True)
                self._stack.push(result)
                self._new_x = True
                self.update_display()
            else:
                self._new_x = True
                self.error()
        else:
            self.no_arg('x')

    def btn_operation_two_arg(self, operation):
        """Function to connect all two argumnts buttons

        Args:
            operation (str): two args button label -> +, -, *, /, %, y^x, mod
        """
        _error = False
        result = 0
        x_value = ''
        y_value = ''
        if not self._stack.peek_x():
            self.no_arg('x')
        elif self._stack.peek_y():
            x_value = self._stack.pop()
            y_value = self._stack.pop()
            try:
                match operation:
                    case '+':
                        result = locale.atof(y_value) + locale.atof(x_value)
                    case '-':
                        result = locale.atof(y_value) - locale.atof(x_value)
                    case '*':
                        result = locale.atof(y_value) * locale.atof(x_value)
                    case '/':
                        result = locale.atof(y_value) / locale.atof(x_value)
                    case '%':
                        result = locale.atof(y_value) * (locale.atof(x_value) / 100)
                    case 'y^x':
                        if self._shift:
                            result = locale.atof(y_value) ** (1.0 / locale.atof(x_value))
                            self.btn_shift()
                        else:
                            result = locale.atof(y_value) ** locale.atof(x_value)
                    case 'mod':
                        result = locale.atof(y_value) % locale.atof(x_value)
                    case _:
                        _error = True
            except Exception:
                _error = True
            if not _error:
                if result > 999999999999:
                    result = locale.format_string('%.8e', result, grouping=True)
                else:
                    result = locale.format_string('%.12g', result, grouping=True)
                self._stack.push(result)
                self.update_display()
            else:
                self._view.y_display.setText('')
                self.error()
        else:
            self.no_arg('y')
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
        if self._stack.is_empty():
            self._stack.push('0')
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
            if self._stack.peek_y():
                self._stack.swap()
                self.update_display()
            else:
                self.no_arg('y')
            self._new_x = True

    def btn_enter(self):
        """Function to connect the ENTER buttton
        Enter a number to the stack, duplicates it and waits for a new number
        """
        self._stack.push(self._stack.peek_x())
        self.update_display()
        self._after_enter = True

    def btn_back(self):
        """Function to connect the BACKSPACE button
        Remove the last caracter from the last entrie in the stack
        """
        if self._stack.peek_x():
            x_value = self._stack.pop()[:-1]
            if x_value == '':
                self._stack.push('0')
            elif x_value:
                if x_value.endswith(('.', ',')):
                    x_value = x_value[:-1]
                x_value = self.format_number(x_value)
                self._stack.push(x_value)
            self.update_display()

    def btn_shift(self):
        """Function to connect the SHIFT button
        Toggle (on/off) the shift button
        """
        self._shift = False if self._shift else True
        if self._shift:
            self._view.shift_label.setText('SHIFT')
        else:
            self._view.shift_label.setText('')

    def btn_pi(self):
        """Function to connect the PI button
        Insert the pi number in the stack
        """
        number = round(math.pi, 12)
        self._stack.push(locale.format_string('%.12g', number, grouping=True))
        self._new_x = True
        self.update_display()

    def btn_e(self):
        """Function to connect the E button
        Insert the e number in the stack
        """
        number = round(math.e, 12)
        self._stack.push(locale.format_string('%.12g', number, grouping=True))
        self._new_x = True
        self.update_display()

    def btn_drg(self):
        """Function to connect the DRG button
        Change or convert degrees units (DEG/GRAD/RAD)
        """
        if self._shift:
            x_value = self._stack.pop()
        else:
            x_value = None
        match self._angle_mesurement:
            case 'DEG':
                self._angle_mesurement = 'RAD'
                if x_value:
                    self.btn_shift()
                    self._stack.push(locale.format_string('%.12g', math.radians(locale.atof(x_value)), grouping=True))
            case 'RAD':
                self._angle_mesurement = 'GRAD'
                if x_value:
                    self.btn_shift()
                    self._stack.push(locale.format_string('%.12g', math.degrees(locale.atof(x_value) * 400 / 360), grouping=True))
            case _:
                self._angle_mesurement = 'DEG'
                if x_value:
                    self.btn_shift()
                    self._stack.push(locale.format_string('%.12g', locale.atof(x_value) * 360 / 400, grouping=True))
        self.update_display()

    def error(self):
        """Show 'ERROR' in the display"""
        self._view.x_display.setText('ERROR')
        
    def format_number(self, number):
        number = locale.atof(number)
        print(f'Before: {number}')
        number = locale.format_string('%.12g', number, grouping=True)
        print(f'After: {number}')
        
        return number


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
        """Connect all buttons with QT signals
        """
        # Keyboard keys not directly shown in the calculator
        self._view.key_signal.connect(self._model.key_pressed)  # using personalized signal key_signal

        # Numbers buttons
        self._view.btn_zero.clicked.connect(partial(self._model.btn_number, '0'))
        self._view.btn_one.clicked.connect(partial(self._model.btn_number, '1'))
        self._view.btn_two.clicked.connect(partial(self._model.btn_number, '2'))
        self._view.btn_three.clicked.connect(partial(self._model.btn_number, '3'))
        self._view.btn_four.clicked.connect(partial(self._model.btn_number, '4'))
        self._view.btn_five.clicked.connect(partial(self._model.btn_number, '5'))
        self._view.btn_six.clicked.connect(partial(self._model.btn_number, '6'))
        self._view.btn_seven.clicked.connect(partial(self._model.btn_number, '7'))
        self._view.btn_eight.clicked.connect(partial(self._model.btn_number, '8'))
        self._view.btn_nine.clicked.connect(partial(self._model.btn_number, '9'))
        self._view.btn_decimal.clicked.connect(partial(self._model.btn_number, ','))

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
        self._view.btn_add.clicked.connect(partial(self._model.btn_operation_two_arg, '+'))
        self._view.btn_minus.clicked.connect(partial(self._model.btn_operation_two_arg, '-'))
        self._view.btn_multiply.clicked.connect(partial(self._model.btn_operation_two_arg, '*'))
        self._view.btn_divide.clicked.connect(partial(self._model.btn_operation_two_arg, '/'))
        self._view.btn_percent.clicked.connect(partial(self._model.btn_operation_two_arg, '%'))
        self._view.btn_y_exp_x.clicked.connect(partial(self._model.btn_operation_two_arg, 'y^x'))
        self._view.btn_mod.clicked.connect(partial(self._model.btn_operation_two_arg, 'mod'))

        # One arg operation buttons
        self._view.btn_change_sign.clicked.connect(partial(self._model.btn_operation_one_arg, '+/-'))
        self._view.btn_x_inv.clicked.connect(partial(self._model.btn_operation_one_arg, '1/x'))
        self._view.btn_sqrt.clicked.connect(partial(self._model.btn_operation_one_arg, 'sqrt'))
        self._view.btn_sin.clicked.connect(partial(self._model.btn_operation_one_arg, 'sin'))
        self._view.btn_cos.clicked.connect(partial(self._model.btn_operation_one_arg, 'cos'))
        self._view.btn_tan.clicked.connect(partial(self._model.btn_operation_one_arg, 'tan'))
        self._view.btn_log.clicked.connect(partial(self._model.btn_operation_one_arg, 'log'))
        self._view.btn_ln.clicked.connect(partial(self._model.btn_operation_one_arg, 'ln'))


def main():
    """PyRPN's main function"""
    pyrpn_app = qtw.QApplication([])
    pyrpn_window = PyRpnWindow()
    pyrpn_window.show()
    PyRpn(pyrpn_window, PyRpnEvaluate(pyrpn_window))
    sys.exit(pyrpn_app.exec())


if __name__ == "__main__":
    main()
