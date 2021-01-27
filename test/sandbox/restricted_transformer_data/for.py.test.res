
def myfunc():
    _check_assign_name_('a')
    for a in _getiter_(b):
        pass
    _check_assign_name_('a')
    _check_assign_name_('b')
    _check_assign_name_('c')
    _check_assign_name_('d')
    _check_assign_name_('e')
    _check_assign_name_('f')
    for a, (b, c, (d, (e, f))) in _iter_unpack_sequence_(b, {'childs': ((1,
        {'childs': ((2, {'childs': ((1, {'childs': (), 'min_len': 2}),),
        'min_len': 2}),), 'min_len': 3}),), 'min_len': 2}, _getiter_):
        pass
