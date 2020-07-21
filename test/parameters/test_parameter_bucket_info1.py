from pyri.parameters.yaml import _bucket_info_schema, _load_bucket_info
import yamale
import pkg_resources

def test_parameter_bucket_info_schema():
    # Validate test schema against schema... schema

    test_info1_str = pkg_resources.resource_string(__name__, "test_parameter_bucket_info1.yml").decode("utf-8")
    test_info1_data = yamale.make_data(content = test_info1_str)
    test_info1_data0 = test_info1_data
    if isinstance(test_info1_data,list):
        test_schema1_data0 = test_info1_data[0]
    yamale.validate(_bucket_info_schema, [test_schema1_data0])

def test_load_parameter_bucket_info():
    test_bucket_info1_str = pkg_resources.resource_string(__name__, "test_parameter_bucket_info1.yml").decode("utf-8")

    bucket_info, group_infos = _load_bucket_info(test_bucket_info1_str)

    print(bucket_info)
    print(group_infos)
   