_print = _print_(_getattr_)


def testfunc():
    _check_assign_name_('a')
    a = _check_return_(_getattr_(b, 'c'))
    _check_assign_name_('a')
    a = _check_return_(_getattr_(_check_return_(_getattr_(b, 'c')), 'd'))
    _check_assign_name_('a')
    a = _check_return_(_getitem_(_check_return_(_getattr_(b, 'c')), e))
    _check_assign_name_('a')
    a = _check_return_(_getattr_(_check_return_(_getitem_(_check_return_(
        _getattr_(b, 'c')), e)), 'd'))
    _write_(b).c = a
    _write_(_check_return_(_getattr_(b, 'c'))).d = a
    _write_(_check_return_(_getattr_(b, 'c')))[e] = a
    _write_(_check_return_(_getitem_(_check_return_(_getattr_(b, 'c')), e))
        ).d = a
