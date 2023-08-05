import json
import logging
from copy import deepcopy
from os import environ

import pytest

LOGGER = logging.getLogger(__name__)


@pytest.fixture()
def actual_results(tmp_path):
    LOGGER.info('Preparing actual results...')
    with open(tmp_path / 'test_data_out.json', 'r') as f:
        results = json.load(f)
    return [{k: v for k, v in result.items() if k in ['key', 'value']} for result in results]


@pytest.fixture()
def expected_results(map_expected_output):
    LOGGER.info('Preparing expected results...')
    return [{k: v for k, v in message.items() if k in ['key', 'value']} for message in map_expected_output]


def remove_fields_from_dict(dict_to_update, fields_to_ignore):
    new_dict = deepcopy(dict_to_update)
    if hasattr(dict_to_update, 'items'):
        for key, value in dict_to_update.items():
            if key in fields_to_ignore:
                new_dict.pop(key)
            if isinstance(value, dict):
                new_value = remove_fields_from_dict(value, fields_to_ignore)
                new_dict[key] = new_value
    return new_dict


def validate_results(actual_results, expected_results, fields_to_ignore=None):
    LOGGER.info('Validating results...')
    try:
        if fields_to_ignore:
            expected_results = [remove_fields_from_dict(record, fields_to_ignore) for record in expected_results]
            actual_results = [remove_fields_from_dict(record, fields_to_ignore) for record in actual_results]
        for expected in expected_results:
            assert expected in actual_results
        LOGGER.info('TEST SUCCESS!')
    except AssertionError:
        LOGGER.info(
            f"TEST FAILURE =(\n\nEXPECTED=\n{json.dumps(expected_results, indent=4)}\n\nACTUAL:\n{json.dumps(actual_results, indent=4)}")
        raise
