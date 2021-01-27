def myfunc():
    try:
        pass
    except Exception:
        pass
    try:
        pass
    except:
        pass
    _check_assign_name_('a')
    _check_assign_name_('b')
    try:
        pass
    except Exception as a:
        pass
    except OtherException as b:
        pass
