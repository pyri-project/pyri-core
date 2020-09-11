_print = _print_(_getattr_)


def testfunc():
    del _write_(b).c
    del _write_(_check_return_(_getattr_(b, 'c'))).d
    del _write_(_check_return_(_getattr_(b, 'c')))[e]
    del _write_(_check_return_(_getitem_(_check_return_(_getattr_(b, 'c')), e))
        ).d
    del _write_(b)[10]
    del _write_(b)[1:10:2]
    del _write_(b)[1:_check_return_(-_check_unary_op_allowed_(1)):10]
    del _write_(_check_return_(_getattr_(b, 'c')))[10]
    del _write_(_check_return_(_getitem_(_check_return_(_getattr_(b, 'c')),
        slice(10, 20, None)))).d
    del _write_(_check_return_(_getattr_(b, 'c')))[e]
    del _write_(_check_return_(_getitem_(_check_return_(_getattr_(b, 'c')),
        (slice(e, 1, None), slice(10, 20, None))))).d
