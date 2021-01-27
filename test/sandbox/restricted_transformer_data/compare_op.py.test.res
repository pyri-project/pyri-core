def myfunc():
    _check_assign_name_('a')
    a = _check_return_(_check_compare_allowed_(b) == _check_compare_allowed_(c)
        )
    _check_assign_name_('a')
    a = _check_return_(_check_compare_allowed_(b) != _check_compare_allowed_(c)
        )
    _check_assign_name_('a')
    a = _check_return_(_check_compare_allowed_(b) < _check_compare_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_compare_allowed_(b) <= _check_compare_allowed_(c)
        )
    _check_assign_name_('a')
    a = _check_return_(_check_compare_allowed_(b) > _check_compare_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_compare_allowed_(b) >= _check_compare_allowed_(c)
        )
    _check_assign_name_('a')
    a = _check_return_(_check_compare_allowed_(b) is _check_compare_allowed_(c)
        )
    _check_assign_name_('a')
    a = _check_return_(_check_compare_allowed_(b) is not
        _check_compare_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_compare_allowed_(b) in _check_compare_allowed_(c)
        )
    _check_assign_name_('a')
    a = _check_return_(_check_compare_allowed_(b) not in
        _check_compare_allowed_(c))
    _check_assign_name_('a')
    a = _check_return_(_check_bool_op_allowed_(_check_return_(
        _check_compare_allowed_(b) == _check_compare_allowed_(c))) and
        _check_bool_op_allowed_(_check_return_(_check_compare_allowed_(b) >
        _check_compare_allowed_(c) < _check_compare_allowed_(d))) and
        _check_bool_op_allowed_(_check_return_(_check_compare_allowed_(e) >
        _check_compare_allowed_(f) > _check_compare_allowed_(g))) and
        _check_bool_op_allowed_(_check_return_(_check_compare_allowed_(e) >
        _check_compare_allowed_(_check_return_(_check_compare_allowed_(f) >
        _check_compare_allowed_(g))))))
