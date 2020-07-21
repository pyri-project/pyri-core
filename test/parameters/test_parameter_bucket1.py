from pyri.parameters import YamlParameterBucket
from pyri.parameters import ParameterBucketScope
from pyri.parameters.yaml import _group_info_schema, _load_group_info
import pkg_resources
import os
import pytest
import yaml

@pytest.mark.asyncio
async def test_yaml_parameter_bucket(tmpdir):
    
    test_bucket_info1_str = pkg_resources.resource_string(__name__, "test_parameter_bucket_info1.yml").decode("utf-8")

    bucket = YamlParameterBucket(test_bucket_info1_str, tmpdir, ParameterBucketScope.CORE)
    bucket_name = (await bucket.get_bucket_info()).name
    assert bucket_name == "test_parameter_bucket_info"

    groups_info = await bucket.get_groups_info()
    assert len(groups_info) == 1
    assert groups_info[0].name == "test_parameter_group_info"

    group1 = await bucket.get_group("test_parameter_group_info")
    await group1.set_param("param1", "this is a test value")



