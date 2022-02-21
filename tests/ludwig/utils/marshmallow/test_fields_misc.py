#! /usr/bin/env python
# Copyright (c) 2020 Uber Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from typing import Dict, List, Optional, Tuple, Union

import pytest
from marshmallow.exceptions import ValidationError as MarshmallowValidationError
from marshmallow_dataclass import dataclass
from marshmallow_jsonschema import JSONSchema as js

import ludwig.utils.schema_utils as lusutils
from ludwig.modules.reduction_modules import reduce_mode_registry
from ludwig.utils.torch_utils import initializer_registry


def get_marshmallow_from_dataclass_field(dfield):
    """Helper method for checking marshmallow metadata succinctly."""
    return dfield.metadata["marshmallow_field"]


def test_InitializerOptions():
    # Test default case:
    initializer_registry_set = set(initializer_registry.keys())
    default_initializer_options = get_marshmallow_from_dataclass_field(lusutils.InitializerOptions())
    assert default_initializer_options.default is None
    assert default_initializer_options.allow_none is True
    assert set(default_initializer_options.validate.choices) == initializer_registry_set

    # Test normal case:
    initializer_options = get_marshmallow_from_dataclass_field(lusutils.InitializerOptions("zeros"))
    assert initializer_options.default == "zeros"
    assert initializer_options.allow_none is True
    assert set(initializer_options.validate.choices) == initializer_registry_set

    # Test invalid default case:
    with pytest.raises(MarshmallowValidationError):
        lusutils.InitializerOptions("test")

    # Test creating a schema with default options:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[str] = lusutils.InitializerOptions()

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": "test"})

    assert CustomTestSchema.Schema().load({}).foo is None

    # Test creating a schema with set default:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[str] = lusutils.InitializerOptions("zeros")

    assert CustomTestSchema.Schema().load({}).foo == "zeros"
    assert CustomTestSchema.Schema().load({"foo": "uniform"}).foo == "uniform"


def test_ReductionOptions():
    # Test default case:
    default_reduction_options = get_marshmallow_from_dataclass_field(lusutils.ReductionOptions())
    assert default_reduction_options.default is None
    assert default_reduction_options.allow_none is True
    assert set(default_reduction_options.validate.choices) == set(list(reduce_mode_registry) + [None])

    # Test normal case:
    reduction_options = get_marshmallow_from_dataclass_field(lusutils.ReductionOptions("concat"))
    assert reduction_options.default == "concat"
    assert reduction_options.allow_none is True
    assert set(reduction_options.validate.choices) == set(list(reduce_mode_registry) + [None])

    # Test invalid default case:
    with pytest.raises(MarshmallowValidationError):
        lusutils.ReductionOptions("dog")

    # Test creating a schema with default options:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[str] = lusutils.ReductionOptions()

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": "test"})

    assert CustomTestSchema.Schema().load({}).foo is None

    # Test creating a schema with set default:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[str] = lusutils.ReductionOptions("concat")

    assert CustomTestSchema.Schema().load({}).foo == "concat"
    assert CustomTestSchema.Schema().load({"foo": "sum"}).foo == "sum"


def test_RegularizerOptions():
    # Test default case:
    default_regularizer_options = get_marshmallow_from_dataclass_field(lusutils.RegularizerOptions())
    assert default_regularizer_options.default is None
    assert default_regularizer_options.allow_none is True
    assert set(default_regularizer_options.validate.choices) == {"l1", "l2", "l1_l2", None}

    # Test normal case:
    regularizer_options = get_marshmallow_from_dataclass_field(lusutils.RegularizerOptions("l1", False))
    assert regularizer_options.default == "l1"
    assert regularizer_options.allow_none is False
    assert set(regularizer_options.validate.choices) == {"l1", "l2", "l1_l2"}

    # Test invalid default case:
    with pytest.raises(MarshmallowValidationError):
        lusutils.RegularizerOptions("dog")

    # Test creating a schema with default options:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[str] = lusutils.RegularizerOptions()

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": "test"})

    assert CustomTestSchema.Schema().load({}).foo is None

    # Test creating a schema with set default:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[str] = lusutils.RegularizerOptions("l2")

    assert CustomTestSchema.Schema().load({}).foo == "l2"
    assert CustomTestSchema.Schema().load({"foo": "l1"}).foo == "l1"


def test_StringOptions():
    # Test empty provided options:
    test_options = []
    with pytest.raises(MarshmallowValidationError):
        lusutils.StringOptions(test_options)

    # Test cases of default conflicting with allowed options:
    test_options = ["one"]
    with pytest.raises(MarshmallowValidationError):
        lusutils.StringOptions(test_options, default="two")

    test_options = ["one"]
    with pytest.raises(MarshmallowValidationError):
        lusutils.StringOptions(test_options, default=None, nullable=False)

    # Test metadata matches expected defaults after field creation (null allowed):
    string_options = get_marshmallow_from_dataclass_field(lusutils.StringOptions(test_options))
    assert string_options.default is None
    assert string_options.allow_none is True
    assert string_options.validate.choices == ["one", None]

    # Test metadata matches expected defaults after field creation (null disallowed):
    string_options = get_marshmallow_from_dataclass_field(
        lusutils.StringOptions(test_options, default="one", nullable=False)
    )
    assert string_options.default == "one"
    assert string_options.allow_none is False
    # Marshmallow still adds 'None' as a valid choice internally:
    assert string_options.validate.choices == ["one", None]

    # Test creating a schema with simple option, null allowed:
    test_options = ["one"]

    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[str] = lusutils.StringOptions(test_options)

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": "test"})

    assert CustomTestSchema.Schema().load({}).foo is None
    assert CustomTestSchema.Schema().load({"foo": None}).foo is None
    assert CustomTestSchema.Schema().load({"foo": "one"}).foo == "one"

    # Test creating a schema with simple option, null not allowed:
    test_options = ["one"]

    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: str = lusutils.StringOptions(test_options, "one", nullable=False)

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": None})


def test_PositiveInteger():
    # Test metadata matches expected defaults after field creation (null allowed):
    default_positive_integer = get_marshmallow_from_dataclass_field(lusutils.PositiveInteger())
    assert default_positive_integer.default is None
    assert default_positive_integer.allow_none is True
    assert default_positive_integer.validate.min == 1

    # Test default value validation:
    with pytest.raises(MarshmallowValidationError):
        lusutils.PositiveInteger("test")

    with pytest.raises(MarshmallowValidationError):
        lusutils.PositiveInteger(-1)

    with pytest.raises(MarshmallowValidationError):
        lusutils.PositiveInteger(1.0)

    with pytest.raises(MarshmallowValidationError):
        lusutils.PositiveInteger(1.1)

    # Test metadata matches expected defaults after field creation (null disallowed):
    positive_integer = get_marshmallow_from_dataclass_field(lusutils.PositiveInteger(1))
    assert positive_integer.default == 1
    assert positive_integer.allow_none is False
    assert positive_integer.validate.min == 1

    # Test creating a normal schema with null not allowed:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: int = lusutils.PositiveInteger(1)

    assert CustomTestSchema.Schema().load({}).foo == 1
    assert CustomTestSchema.Schema().load({"foo": 2}).foo == 2

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": None})

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": 0})

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": 0.1})

    # Test creating a schema with null allowed:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[int] = lusutils.PositiveInteger()

    assert CustomTestSchema.Schema().load({}).foo is None
    assert CustomTestSchema.Schema().load({"foo": None}).foo is None


def test_NonNegativeInteger():
    # Test metadata matches expected defaults after field creation (null allowed):
    default_nonnegative_integer = get_marshmallow_from_dataclass_field(lusutils.NonNegativeInteger())
    assert default_nonnegative_integer.default is None
    assert default_nonnegative_integer.allow_none is True
    assert default_nonnegative_integer.validate.min == 0

    # Test default value validation:
    with pytest.raises(MarshmallowValidationError):
        lusutils.NonNegativeInteger("test")

    with pytest.raises(MarshmallowValidationError):
        lusutils.NonNegativeInteger(-1)

    with pytest.raises(MarshmallowValidationError):
        lusutils.NonNegativeInteger(0.0)

    with pytest.raises(MarshmallowValidationError):
        lusutils.NonNegativeInteger(0.1)

    # Test metadata matches expected defaults after field creation (null disallowed):
    nonnegative_integer = get_marshmallow_from_dataclass_field(lusutils.NonNegativeInteger(0))
    assert nonnegative_integer.default == 0
    assert nonnegative_integer.allow_none is False
    assert nonnegative_integer.validate.min == 0

    # Test creating a normal schema with null not allowed:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: int = lusutils.NonNegativeInteger(0)

    assert CustomTestSchema.Schema().load({}).foo == 0
    assert CustomTestSchema.Schema().load({"foo": 1}).foo == 1

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": None})

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": -1})

    # Test creating a schema with null allowed:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[int] = lusutils.NonNegativeInteger()

    assert CustomTestSchema.Schema().load({}).foo is None
    assert CustomTestSchema.Schema().load({"foo": None}).foo is None


def test_IntegerRange():
    # Test metadata matches expected defaults after field creation (null allowed):
    default_integer_range = get_marshmallow_from_dataclass_field(lusutils.IntegerRange())
    assert default_integer_range.default is None
    assert default_integer_range.allow_none is True
    assert default_integer_range.validate.min is None
    assert default_integer_range.validate.max is None
    assert default_integer_range.validate.min_inclusive is True
    assert default_integer_range.validate.max_inclusive is True

    # Test default value validation:
    with pytest.raises(MarshmallowValidationError):
        lusutils.IntegerRange("test")

    with pytest.raises(MarshmallowValidationError):
        lusutils.IntegerRange(0.0)

    with pytest.raises(MarshmallowValidationError):
        lusutils.IntegerRange(0.1)

    with pytest.raises(MarshmallowValidationError):
        lusutils.IntegerRange(0, min=0, max=1, min_inclusive=False)

    # Test metadata matches expected defaults after field creation (null disallowed):
    integer_range = get_marshmallow_from_dataclass_field(lusutils.IntegerRange(0))
    assert integer_range.default == 0
    assert integer_range.allow_none is False
    assert integer_range.validate.min is None
    assert integer_range.validate.max is None
    assert integer_range.validate.min_inclusive is True
    assert integer_range.validate.max_inclusive is True

    integer_range = get_marshmallow_from_dataclass_field(lusutils.IntegerRange(0, min=-1, max=1))
    assert integer_range.default == 0
    assert integer_range.allow_none is False
    assert integer_range.validate.min == -1
    assert integer_range.validate.max == 1
    assert integer_range.validate.min_inclusive is True
    assert integer_range.validate.max_inclusive is True

    # Test creating a schema with null allowed:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[int] = lusutils.IntegerRange()

    assert CustomTestSchema.Schema().load({}).foo is None
    assert CustomTestSchema.Schema().load({"foo": None}).foo is None

    # Test creating a normal schema on interval (-1, 1]
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[int] = lusutils.IntegerRange(0, min=-1, max=1, min_inclusive=False)

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": -1})

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": 0.1})

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": 1.0})

    assert CustomTestSchema.Schema().load({"foo": 1}).foo == 1


def test_NonNegativeFloat():
    # Test metadata matches expected defaults after field creation (null allowed):
    default_nonnegative_float = get_marshmallow_from_dataclass_field(lusutils.NonNegativeFloat())
    assert default_nonnegative_float.default is None
    assert default_nonnegative_float.allow_none is True
    assert default_nonnegative_float.validate.min == 0

    # Test default value validation:
    with pytest.raises(MarshmallowValidationError):
        lusutils.NonNegativeFloat("test")

    with pytest.raises(MarshmallowValidationError):
        lusutils.NonNegativeFloat(-1)

    # Negative zero case:
    assert get_marshmallow_from_dataclass_field(lusutils.NonNegativeFloat(-0.0)).default == 0

    # Test metadata matches expected defaults after field creation (null disallowed):
    nonnegative_float = get_marshmallow_from_dataclass_field(lusutils.NonNegativeInteger(0))
    assert nonnegative_float.default == 0
    assert nonnegative_float.allow_none is False
    assert nonnegative_float.validate.min == 0

    # Test creating a normal schema with null not allowed:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: int = lusutils.NonNegativeFloat(0.0)

    assert CustomTestSchema.Schema().load({}).foo == 0
    assert CustomTestSchema.Schema().load({"foo": 0.1}).foo == 0.1

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": None})

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": -1.0})

    assert CustomTestSchema.Schema().load({"foo": 1}).foo == 1.0

    # Test creating a schema with null allowed:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[int] = lusutils.NonNegativeInteger()

    assert CustomTestSchema.Schema().load({}).foo is None
    assert CustomTestSchema.Schema().load({"foo": None}).foo is None


def test_FloatRange():
    # Test metadata matches expected defaults after field creation (null allowed):
    default_float_range = get_marshmallow_from_dataclass_field(lusutils.FloatRange())
    assert default_float_range.default is None
    assert default_float_range.allow_none is True
    assert default_float_range.validate.min is None
    assert default_float_range.validate.max is None
    assert default_float_range.validate.min_inclusive is True
    assert default_float_range.validate.max_inclusive is True

    # Test default value validation:
    with pytest.raises(MarshmallowValidationError):
        lusutils.FloatRange("test")

    with pytest.raises(MarshmallowValidationError):
        lusutils.FloatRange(0, min=0, max=1, min_inclusive=False)

    # Test metadata matches expected defaults after field creation (null disallowed):
    float_range = get_marshmallow_from_dataclass_field(lusutils.FloatRange(0))
    assert float_range.default == 0
    assert float_range.allow_none is False
    assert float_range.validate.min is None
    assert float_range.validate.max is None
    assert float_range.validate.min_inclusive is True
    assert float_range.validate.max_inclusive is True

    float_range = get_marshmallow_from_dataclass_field(lusutils.FloatRange(0, min=-1, max=1))
    assert float_range.default == 0
    assert float_range.allow_none is False
    assert float_range.validate.min == -1
    assert float_range.validate.max == 1
    assert float_range.validate.min_inclusive is True
    assert float_range.validate.max_inclusive is True

    # Test creating a schema with null allowed:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[int] = lusutils.FloatRange()

    assert CustomTestSchema.Schema().load({}).foo is None
    assert CustomTestSchema.Schema().load({"foo": None}).foo is None

    # Test creating a normal schema on interval (-1, 1]
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[int] = lusutils.FloatRange(0, min=-1, max=1, min_inclusive=False)

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": -1})

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": -1.0})

    assert CustomTestSchema.Schema().load({"foo": 0.1}).foo == 0.1
    assert CustomTestSchema.Schema().load({"foo": 1.0}).foo == 1
    assert CustomTestSchema.Schema().load({"foo": 1}).foo == 1


def test_Dict():
    # Test metadata matches expected defaults after field creation (null allowed):
    default_dict = get_marshmallow_from_dataclass_field(lusutils.Dict())
    assert default_dict.default is None
    assert default_dict.allow_none is True

    default_dict = get_marshmallow_from_dataclass_field(lusutils.Dict({"a": "b"}))
    assert default_dict.default == {"a": "b"}
    assert default_dict.allow_none is True

    # Test default value validation:
    with pytest.raises(MarshmallowValidationError):
        lusutils.Dict("test")

    with pytest.raises(MarshmallowValidationError):
        lusutils.Dict(0)

    with pytest.raises(MarshmallowValidationError):
        lusutils.Dict({1: "invalid", "2": "valid"})

    # Test simple schema creation:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[Dict] = lusutils.Dict()

    assert CustomTestSchema.Schema().load({}).foo is None
    assert CustomTestSchema.Schema().load({"foo": {"a": "b"}}).foo == {"a": "b"}

    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[Dict] = lusutils.Dict({"a": "b"})

    assert CustomTestSchema.Schema().load({}).foo == {"a": "b"}


def test_DictList():
    # Test metadata matches expected defaults after field creation (null allowed):
    default_dictlist = get_marshmallow_from_dataclass_field(lusutils.DictList())
    assert default_dictlist.default is None
    assert default_dictlist.allow_none is True

    default_dictlist = get_marshmallow_from_dataclass_field(lusutils.DictList([{"a": "b"}]))
    assert default_dictlist.default == [{"a": "b"}]
    assert default_dictlist.allow_none is True

    # Test default value validation:
    with pytest.raises(MarshmallowValidationError):
        lusutils.DictList("test")

    with pytest.raises(MarshmallowValidationError):
        lusutils.DictList(0)

    with pytest.raises(MarshmallowValidationError):
        lusutils.DictList({1: "invalid", "2": "valid"})

    with pytest.raises(MarshmallowValidationError):
        lusutils.DictList([{1: "invalid", "2": "valid"}])

    # Test simple schema creation:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[List] = lusutils.DictList()

    assert CustomTestSchema.Schema().load({}).foo is None
    assert CustomTestSchema.Schema().load({"foo": [{"a": "b"}]}).foo == [{"a": "b"}]

    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Optional[List] = lusutils.DictList([{"a": "b"}])

    assert CustomTestSchema.Schema().load({}).foo == [{"a": "b"}]


def test_Embed():
    # Test metadata matches expected defaults after field creation (null allowed):
    default_embed = get_marshmallow_from_dataclass_field(lusutils.Embed())
    assert default_embed.default is None
    assert default_embed.allow_none is True

    # Test simple schema creation:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Union[None, str, int] = lusutils.Embed()

    # Test null/empty loading cases:
    assert CustomTestSchema.Schema().load({}).foo is None
    assert CustomTestSchema.Schema().load({"foo": None}).foo is None

    # Test valid strings/numbers:
    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": "not_add"})

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": {}})

    assert CustomTestSchema.Schema().load({"foo": "add"}).foo == "add"
    assert CustomTestSchema.Schema().load({"foo": 1}).foo == 1

    # Test expected schema dump:
    raw_embed_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {
            "CustomTestSchema": {
                "properties": {
                    "foo": {"oneOf": [{"type": "string", "enum": ["add"]}, {"type": "integer"}, {"type": "null"}]}
                },
                "type": "object",
                "additionalProperties": False,
            }
        },
        "$ref": "#/definitions/CustomTestSchema",
    }

    assert js().dump(CustomTestSchema.Schema()) == raw_embed_schema


def test_InitializerOrDict():
    # Test metadata matches expected defaults after field creation (null allowed):
    default_initializerordict = get_marshmallow_from_dataclass_field(lusutils.InitializerOrDict())
    assert default_initializerordict.default == "xavier_uniform"
    assert default_initializerordict.allow_none is True

    initializerordict = get_marshmallow_from_dataclass_field(lusutils.InitializerOrDict("zeros"))
    assert initializerordict.default == "zeros"
    assert initializerordict.allow_none is True

    # Test default value validation:
    with pytest.raises(MarshmallowValidationError):
        lusutils.InitializerOrDict("test")

    # Test simple schema creation:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Union[None, str, Dict] = lusutils.InitializerOrDict()

    # Test invalid non-dict loads:
    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": 1})

    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": "test"})

    # Test valid non-dict loads:
    assert CustomTestSchema.Schema().load({}).foo == "xavier_uniform"
    assert CustomTestSchema.Schema().load({"foo": None}).foo is None
    assert CustomTestSchema.Schema().load({"foo": "zeros"}).foo == "zeros"

    # Test invalid dict loads:
    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": {"a": "b"}})
    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": {"type": "invalid"}})

    # Test valid dict loads:
    assert CustomTestSchema.Schema().load({"foo": {"type": None}}).foo == {"type": None}
    assert CustomTestSchema.Schema().load({"foo": {"type": "zeros"}}).foo == {"type": "zeros"}
    assert CustomTestSchema.Schema().load({"foo": {"type": None, "a": "b"}}).foo == {"type": None, "a": "b"}

    # Test expected schema dump:
    initializers = list(initializer_registry.keys())
    raw_initializerordict_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {
            "CustomTestSchema": {
                "properties": {
                    "foo": {
                        "oneOf": [
                            {
                                "type": ["string", "null"],
                                "enum": initializers,
                                "default": "xavier_uniform",
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": initializers},
                                },
                                "required": ["type"],
                                "additionalProperties": True,
                            },
                        ]
                    }
                },
                "type": "object",
                "additionalProperties": False,
            }
        },
        "$ref": "#/definitions/CustomTestSchema",
    }
    assert js().dump(CustomTestSchema.Schema()) == raw_initializerordict_schema


def test_FloatRangeTupleDataclassField():
    # Test metadata matches expected defaults after field creation (null not allowed):
    default_floatrange_tuple = get_marshmallow_from_dataclass_field(lusutils.FloatRangeTupleDataclassField())
    assert default_floatrange_tuple.default == (0.9, 0.999)

    # Test dimensional mismatch:
    with pytest.raises(MarshmallowValidationError):
        lusutils.FloatRangeTupleDataclassField(N=3, default=(1, 1))

    # Test default schema creation:
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Tuple[float, float] = lusutils.FloatRangeTupleDataclassField()

    # Test empty load:
    assert CustomTestSchema.Schema().load({}).foo == (0.9, 0.999)

    # Test invalid loads (null, non-float values, wrong dimension):
    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": None})
    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": [1, "test"]})
    with pytest.raises(MarshmallowValidationError):
        CustomTestSchema.Schema().load({"foo": (1, 1, 1)})

    # Test non-default schema (N=3, other custom metadata):
    @dataclass
    class CustomTestSchema(lusutils.BaseMarshmallowConfig):
        foo: Tuple[float, float] = lusutils.FloatRangeTupleDataclassField(N=3, default=(1, 1, 1), min=-10, max=10)

    assert CustomTestSchema.Schema().load({}).foo == (1, 1, 1)
    assert CustomTestSchema.Schema().load({"foo": [2, 2, 2]}).foo == (2, 2, 2)
    assert CustomTestSchema.Schema().load({"foo": (2, 2, 2)}).foo == (2, 2, 2)

    # Test expected schema dump:
    triple_tuple_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {
            "CustomTestSchema": {
                "properties": {
                    "foo": {
                        "type": "array",
                        "prefixItems": [
                            {"type": "number", "minimum": -10, "maximum": 10},
                            {"type": "number", "minimum": -10, "maximum": 10},
                            {"type": "number", "minimum": -10, "maximum": 10},
                        ],
                        "default": (1, 1, 1),
                    }
                },
                "type": "object",
                "additionalProperties": False,
            }
        },
        "$ref": "#/definitions/CustomTestSchema",
    }
    assert js().dump(CustomTestSchema.Schema()) == triple_tuple_schema