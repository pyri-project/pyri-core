from pyri.parameters.yaml import _group_info_schema, _load_group_info
import yamale
import pkg_resources

def test_parameter_group_info_schema():
    # Validate test schema against schema... schema

    test_info1_str = pkg_resources.resource_string(__name__, "test_parameter_group_info1.yml").decode("utf-8")
    test_info1_data = yamale.make_data(content = test_info1_str)
    test_info1_data0 = test_info1_data
    if isinstance(test_info1_data,list):
        test_schema1_data0 = test_info1_data[0]
    yamale.validate(_group_info_schema, [test_schema1_data0])

def test_load_parameter_group_info():
    test_group_info1_str = pkg_resources.resource_string(__name__, "test_parameter_group_info1.yml").decode("utf-8")

    group_info, all_param_schema, param_schema_dict = _load_group_info(test_group_info1_str)

    print(group_info)
    print(all_param_schema)
    print(param_schema_dict)