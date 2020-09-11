_print = _print_(_getattr_)


def myfunc():
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) +
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) -
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) *
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) /
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) //
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) %
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) **
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) <<
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) >>
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) |
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) ^
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) &
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) @
        _check_binary_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(_check_return_(
        _check_binary_op_allowed_(_check_return_(_check_binary_op_allowed_(
        b) * _check_binary_op_allowed_(c))) + _check_binary_op_allowed_(
        _check_return_(_check_binary_op_allowed_(e) //
        _check_binary_op_allowed_(f))))) & _check_binary_op_allowed_(
        _check_return_(_check_binary_op_allowed_(g) @
        _check_binary_op_allowed_(_check_return_(-_check_unary_op_allowed_(
        h))))))
