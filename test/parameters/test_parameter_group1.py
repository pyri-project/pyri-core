from pyri.parameters import YamlParameterGroup, YamlGroupInfoWithSchema
from pyri.parameters.yaml import _group_info_schema, _load_group_info
import pkg_resources
import os
import pytest
import yaml

@pytest.mark.asyncio
async def test_yaml_parameter_group(tmpdir):
    fname1 = os.path.join(tmpdir,"empty_params.yml")

    group_info1_str = pkg_resources.resource_string(__name__, "test_parameter_group_info1.yml").decode("utf-8")
    group_info1, group_schema1, param_schema1 = _load_group_info(group_info1_str)

    with open(fname1, "a+") as f1:

        # Scalar parameter
        params1 = YamlParameterGroup(YamlGroupInfoWithSchema(group_info1, group_schema1, param_schema1), f1)
        param1_val1 = await params1.get_param_or_default("param1")
        assert param1_val1 == "hello world!"    
        param1_val2 = await params1.get_param_or_default("param1","hello world 2")
        assert param1_val2 == "hello world 2"
        param1_val3_res, param1_val3 = await params1.try_get_param("param1")
        assert not param1_val3_res
        await params1.set_param("param1", "hello world 3")
        assert await params1.get_param("param1") == "hello world 3"
        param1_val5_res, param1_val5 = await params1.try_get_param("param1")
        assert param1_val5_res
        assert param1_val5 == "hello world 3"

        # List parameter
        list_param_val1 = await params1.get_param_or_default("list_param")
        assert list_param_val1 is None
        list_param_val1_item1 = await params1.get_param_item_or_default("list_param",1,None)
        assert list_param_val1_item1 is None
        await params1.append_param_item("list_param","item 1")
        list_param_val2 = await params1.get_param("list_param")
        assert(list_param_val2 == ["item 1"])
        await params1.append_param_item("list_param", "item 2")
        await params1.append_param_item("list_param", "item 3")
        await params1.set_param_item("list_param", 1, "item 4")
        list_param_val3_item1 = await params1.get_param_item("list_param",1)
        assert list_param_val3_item1 == "item 4"
        list_param_val3_item2 = await params1.get_param_item("list_param",2)
        assert list_param_val3_item2 == "item 3"
        assert await params1.get_param_item_count("list_param") == 3
        list_param_val3_item0_res, list_param_val3_item0 = await params1.try_get_param_item("list_param",0)
        assert list_param_val3_item0_res
        assert list_param_val3_item0 == "item 1"
        list_param_val3_item4_res, list_param_val4_item0 = await params1.try_get_param_item("list_param",4)
        assert not list_param_val3_item4_res
        await params1.del_param_item("list_param",0)
        list_param_val4 = await params1.get_param("list_param")
        assert list_param_val4 == ["item 4", "item 3"]

        # Numeric list parameter

        with pytest.raises(ValueError):
            await params1.append_param_item("num_list_param", 100)
        num_list_param_val1 = await params1.get_param_or_default("num_list_param")
        await params1.set_param("num_list_param", num_list_param_val1)
        await params1.append_param_item("num_list_param", 100)
        num_list_param_val2 = await params1.get_param("num_list_param")
        assert num_list_param_val2 == [10,9,5.52,1,100]

        # Map parameter

        await params1.set_param_item("map_param", "map_value1", "val 1")
        await params1.set_param_item("map_param", "map_value2", "val 2")
        map_param_val1_value1 = await params1.get_param_item("map_param", "map_value1")
        assert map_param_val1_value1 == "val 1"
        assert await params1.get_param_item_count("map_param") == 2

        # Secret parameter

        secret_param_val1 = await params1.get_param_or_default("secret_param")
        assert secret_param_val1 == "password"
        await params1.set_param("secret_param", "my_password")

    with open(fname1, "r") as f2:
        saved_group1 = yaml.safe_load(f2)

    group_1_str = pkg_resources.resource_string(__name__, "test_parameter_group1.yml").decode("utf-8")
    saved_group2 = yaml.safe_load(group_1_str)

    assert saved_group1 == saved_group2
        