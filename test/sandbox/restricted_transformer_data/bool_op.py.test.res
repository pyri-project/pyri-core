def myfunc():
    _check_assign_name_('a')
    a = _check_return_(_check_bool_op_allowed_(b) and
        _check_bool_op_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_bool_op_allowed_(b) or _check_bool_op_allowed_(c)
        )
    _check_assign_name_('a')
    a = _check_return_(_check_bool_op_allowed_(_check_return_(
        _check_bool_op_allowed_(b) and _check_bool_op_allowed_(c))) or
        _check_bool_op_allowed_(_check_return_(_check_bool_op_allowed_(e) and
        _check_bool_op_allowed_(_check_return_(_check_bool_op_allowed_(f) or
        _check_bool_op_allowed_(g))))))
