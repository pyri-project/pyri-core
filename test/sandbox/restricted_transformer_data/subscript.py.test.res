_print = _print_(_getattr_)


def testfunc():
    _check_assign_name_('a')
    a = _check_return_(_getitem_(b, 10))
    _check_assign_name_('a')
    a = _check_return_(_getitem_(b, slice(1, 10, 2)))
    _check_assign_name_('a')
    a = _check_return_(_getitem_(b, slice(1, _check_return_(-
        _check_unary_op_allowed_(1)), 10)))
    _write_(b)[10] = a
    _write_(b)[1:10:2] = a
    _write_(b)[1:_check_return_(-_check_unary_op_allowed_(1)):10] = a
    _check_assign_name_('a')
    a = _check_return_(_getitem_(_check_return_(_getattr_(b, 'c')), 10))
    _check_assign_name_('a')
    a = _check_return_(_getattr_(_check_return_(_getitem_(_check_return_(
        _getattr_(b, 'c')), slice(10, 20, None))), 'd'))
    _check_assign_name_('a')
    a = _check_return_(_getitem_(_check_return_(_getattr_(b, 'c')), e))
    _check_assign_name_('a')
    a = _check_return_(_getattr_(_check_return_(_getitem_(_check_return_(
        _getattr_(b, 'c')), (slice(e, 1, None), slice(10, 20, None)))), 'd'))
    _write_(_check_return_(_getattr_(b, 'c')))[10] = a
    _write_(_check_return_(_getitem_(_check_return_(_getattr_(
        _check_return_(_getitem_(b, 1)), 'c')), slice(10, 20, None)))).d = a
    _write_(_check_return_(_getattr_(b, 'c')))[e] = a
    _write_(_check_return_(_getattr_(_check_return_(_getitem_(
        _check_return_(_getattr_(b, 'c')), (slice(e, 1, None), slice(0, 20,
        None)))), 'd')))[5] = a
