_print = _print_(_getattr_)


def myfunc():
    _check_return_(a())
    _check_return_(a(b, c))
    _check_return_(a(_check_return_(b(10, 20)), _check_return_(c(30, 40,
        _check_return_(d())))))
