_print = _print_(_getattr_)


def myfunc():
    _check_assign_name_('a')
    a = 1
    _check_assign_name_('b')
    b = _check_return_(+_check_unary_op_allowed_(a))
    _check_assign_name_('b')
    b = _check_return_(-_check_unary_op_allowed_(a))
    _check_assign_name_('b')
    b = _check_return_(~_check_unary_op_allowed_(a))
    _check_assign_name_('b')
    b = _check_return_(not _check_unary_op_allowed_(a))
