# import PyQt6.QtWidgets as qtw
import rpn

import PyQt6.QtWidgets as qtw


def test_two_args_integer_operations():
    _ = qtw.QApplication([])
    pyrpn_window = rpn.PyRpnWindow()
    rpn_obj = rpn.PyRpnEvaluate(pyrpn_window)

    # add operation
    rpn_obj._stack.push('7')
    rpn_obj._stack.push('3')
    rpn_obj.btn_operation_two_arg('+')
    assert rpn_obj._stack.peek_x() == '10'

    # subtract operation
    rpn_obj._stack.push('4')
    rpn_obj.btn_operation_two_arg('-')
    assert rpn_obj._stack.peek_x() == '6'

    # multiply operation
    rpn_obj._stack.push('3')
    rpn_obj.btn_operation_two_arg('*')
    assert rpn_obj._stack.peek_x() == '18'

    # multiply operation
    rpn_obj._stack.push('6')
    rpn_obj.btn_operation_two_arg('/')
    assert rpn_obj._stack.peek_x() == '3'

    # y expoent x operation
    rpn_obj._stack.push('3')
    rpn_obj.btn_operation_two_arg('y^x')
    assert rpn_obj._stack.peek_x() == '27'

    # mod operation
    rpn_obj._stack.push('7')
    rpn_obj.btn_operation_two_arg('mod')
    assert rpn_obj._stack.peek_x() == '6'

    # % operation
    rpn_obj._stack.push('50')
    rpn_obj.btn_operation_two_arg('%')
    assert rpn_obj._stack.peek_x() == '3'

    # y square x operation
    rpn_obj._stack.push('6')
    rpn_obj.btn_operation_two_arg('y^x')
    rpn_obj._stack.push('6')
    rpn_obj._shift = True
    rpn_obj.btn_operation_two_arg('y^x')
    assert rpn_obj._stack.peek_x() == '3'


def test_two_args_float_operations():
    _ = qtw.QApplication([])
    pyrpn_window = rpn.PyRpnWindow()
    rpn_obj = rpn.PyRpnEvaluate(pyrpn_window)

    # sum operation
    rpn_obj._stack.push('6,25')
    rpn_obj._stack.push('3,50')
    rpn_obj.btn_operation_two_arg('+')
    assert rpn_obj._stack.peek_x() == '9,75'

    # subtract operation
    rpn_obj._stack.push('4,55')
    rpn_obj.btn_operation_two_arg('-')
    assert rpn_obj._stack.peek_x() == '5,2'

    # multiply operation
    rpn_obj._stack.push('3,4')
    rpn_obj.btn_operation_two_arg('*')
    assert rpn_obj._stack.peek_x() == '17,68'

    # division operation
    rpn_obj._stack.push('2,5')
    rpn_obj.btn_operation_two_arg('/')
    assert rpn_obj._stack.peek_x() == '7,072'

    # y expoent x operation
    rpn_obj._stack.push('2')
    rpn_obj.btn_operation_two_arg('y^x')
    assert rpn_obj._stack.peek_x() == '50,013184'

    # % operation
    rpn_obj._stack.push('25')
    rpn_obj.btn_operation_two_arg('%')
    assert rpn_obj._stack.peek_x() == '12,503296'

    # y square x operation
    rpn_obj._stack.push('6')
    rpn_obj.btn_operation_two_arg('y^x')
    rpn_obj._stack.push('6')
    rpn_obj._shift = True
    rpn_obj.btn_operation_two_arg('y^x')
    assert rpn_obj._stack.peek_x() == '12,503296'
