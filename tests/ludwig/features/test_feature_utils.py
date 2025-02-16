import torch

from ludwig.features import feature_utils


def test_ludwig_feature_dict():
    feature_dict = feature_utils.LudwigFeatureDict()

    to_module = torch.nn.Module()
    type_module = torch.nn.Module()

    feature_dict["to"] = to_module
    feature_dict["type"] = type_module

    assert iter(feature_dict) is not None
    assert next(feature_dict) is not None
    assert len(feature_dict) == 2
    assert feature_dict.keys() == ["to", "type"]
    assert feature_dict.items() == [("to", to_module), ("type", type_module)]
    assert feature_dict["to"] == to_module

    feature_dict.update({"to_empty": torch.nn.Module()})

    assert len(feature_dict) == 3
    assert [key for key in feature_dict] == ["to", "type", "to_empty"]


def test_ludwig_feature_dict_with_periods():
    feature_dict = feature_utils.LudwigFeatureDict()

    to_module = torch.nn.Module()

    feature_dict["to."] = to_module

    assert feature_dict.keys() == ["to."]
    assert feature_dict.items() == [("to.", to_module)]
    assert feature_dict["to."] == to_module
