def myfunc():
    _check_assign_name_('a')
    a = _check_return_(_check_binary_op_allowed_(b) +
        _check_binary_op_allowed_(c))
    _check_assign_name_('b')
    b = _check_return_(-_check_unary_op_allowed_(c))
    _check_assign_name_('a')
    a = 10
    _check_assign_name_('c')
    _check_assign_name_('d')
    c, d = _unpack_sequence_((100, 200), {'childs': (), 'min_len': 2},
        _getiter_)
    _check_assign_name_('c')
    _check_assign_name_('d')
    _check_assign_name_('e')
    c, (d, e, _write_(f).a) = _unpack_sequence_((100, (200, 300, 400)), {
        'childs': ((1, {'childs': (), 'min_len': 3}),), 'min_len': 2},
        _getiter_)
    _write_(my_var)[10] = 150
    _write_(my_var).a = 100
    _check_assign_name_('b')
    _check_assign_name_('d')
    _write_(_check_return_(_getitem_(_check_return_(_getattr_(
        _check_return_(_getattr_(my_var, 'a')), 'b')), 10))).c, (b, d
        ) = _unpack_sequence_(200, {'childs': ((1, {'childs': (), 'min_len':
        2}),), 'min_len': 2}, _getiter_)
    _check_assign_name_('a')
    a = _check_return_(_getitem_(my_var, 10))
    _check_assign_name_('a')
    a = _check_return_(_check_return_(_getattr_(my_var, 'a'))())
    _check_assign_name_('b')
    b = _check_return_(_getitem_(_check_return_(_getattr_(_check_return_(
        _getattr_(my_var, 'a')), 'b')), 10))
    _check_assign_name_('h')
    h = _check_return_(_check_bool_op_allowed_(a) or
        _check_bool_op_allowed_(_check_return_(_check_bool_op_allowed_(b) and
        _check_bool_op_allowed_(c))))
    _check_assign_name_('h')
    h = _check_return_(_check_compare_allowed_(a) < _check_compare_allowed_
        (b) > _check_compare_allowed_(c))
