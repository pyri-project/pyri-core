from pyri.core import PyriCore


def test_get_default_config_dir():
    from pyri.core.core import _get_default_config_dir
    config_dir = _get_default_config_dir()
    print(config_dir)
