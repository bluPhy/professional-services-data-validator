# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from pandas import DataFrame

from data_validation.consts import VALIDATION_STATUS_FAIL

SAMPLE_CONFIG = {}
SAMPLE_CONFIG_FILTER_STATUS = [
    VALIDATION_STATUS_FAIL,
]

SAMPLE_RESULT_DATA = [
    [0, 1, 2, 3, "Column", "source", "target", "success"],
    [4, 5, 6, 7, "Column", "source", "target", "success"],
    [8, 9, 10, 11, "Column", "source", "target", "fail"],
]
SAMPLE_RESULT_COLUMNS = [
    "A",
    "B",
    "C",
    "D",
    "validation_type",
    "source_agg_value",
    "target_agg_value",
    "validation_status",
]
SAMPLE_RESULT_COLUMNS_FILTER_LIST = [
    "B",
    "D",
    "validation_type",
    "source_agg_value",
    "target_agg_value",
    "validation_status",
]


@pytest.fixture
def module_under_test():
    from data_validation.result_handlers import text

    return text


def test_import(module_under_test):
    """Test import cleanly"""
    assert module_under_test is not None


def test_basic_result_handler(module_under_test):
    """Test basic handler executes"""
    result_df = DataFrame(SAMPLE_RESULT_DATA, columns=SAMPLE_RESULT_COLUMNS)
    format = "csv"
    result_handler = module_under_test.TextResultHandler(
        format, cols_filter_list=SAMPLE_RESULT_COLUMNS_FILTER_LIST
    )

    handler_output = result_handler.execute(result_df)
    assert handler_output["A"].sum() == result_df["A"].sum()


def test_basic_result_handler_filtered_results(module_under_test):
    """Test basic handler executes and shows only failed records"""
    result_df = DataFrame(SAMPLE_RESULT_DATA, columns=SAMPLE_RESULT_COLUMNS)
    format = "table"
    result_handler = module_under_test.TextResultHandler(
        format, SAMPLE_CONFIG_FILTER_STATUS, SAMPLE_RESULT_COLUMNS_FILTER_LIST
    )

    handler_output = result_handler.execute(result_df)
    assert len(handler_output.index) == 1


def test_unsupported_result_format(module_under_test):
    """Check for invalid format"""
    with pytest.raises(ValueError):
        result_df = DataFrame(SAMPLE_RESULT_DATA, columns=SAMPLE_RESULT_COLUMNS)
        format = "foobar"
        result_handler = module_under_test.TextResultHandler(
            format, cols_filter_list=SAMPLE_RESULT_COLUMNS_FILTER_LIST
        )

        handler_output = result_handler.execute(result_df)
        assert handler_output["A"].sum() == result_df["A"].sum()


def test_columns_to_print(module_under_test, capsys):
    """Check for trimmed columns in grid print"""
    result_df = DataFrame(SAMPLE_RESULT_DATA, columns=SAMPLE_RESULT_COLUMNS)
    format = "table"
    result_handler = module_under_test.TextResultHandler(
        format, cols_filter_list=SAMPLE_RESULT_COLUMNS_FILTER_LIST
    )
    result_handler.execute(result_df)

    grid_text = "│A│C││0│2││4│6││8│10│"
    printed_text = capsys.readouterr().out
    print(printed_text)
    printed_text = (
        printed_text.replace("\n", "")
        .replace("'", "")
        .replace(" ", "")
        .replace("╒═════╤═════╕", "")
        .replace("╞═════╪═════╡", "")
        .replace("├─────┼─────┤", "")
        .replace("╘═════╧═════╛", "")
    )
    assert printed_text == grid_text
