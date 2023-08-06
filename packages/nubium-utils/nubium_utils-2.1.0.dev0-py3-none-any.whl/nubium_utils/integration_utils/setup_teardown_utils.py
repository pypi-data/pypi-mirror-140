from datetime import datetime
import json
import logging
from os import environ
from time import sleep
from unittest.mock import patch

import psutil
import pytest

from nubium_utils.confluent_utils import KafkaToolbox
from nubium_schemas.nubium_shared_apps.eloqua import eloqua_retriever_timestamp

LOGGER = logging.getLogger(__name__)


kafka_toolbox = KafkaToolbox()


@pytest.fixture()
def initialize_timestamp_topic():
    LOGGER.info("Initializing timestamp topic...")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    kafka_toolbox.produce_messages(
        topic=environ['TIMESTAMP_TOPIC'],
        schema=eloqua_retriever_timestamp,
        message_list=[dict(headers={"guid": "N/A", "last_updated_by": "dude"}, key="dude_timestamp", value={"timestamp": timestamp})])
    sleep(30)  # wait for app to consume


@pytest.fixture()
def setup_teardown_env_vars(env_vars):
    LOGGER.info("Patching environment variables...")
    env_patch = patch.dict('os.environ', env_vars)
    env_patch.start()
    yield None
    LOGGER.info("Unpatching environment variables...")
    env_patch.stop()


@pytest.fixture()
def setup_app(request):
    # optional args, set via @pytest.mark.paramatrize('setup_app', [{'env_overrides': {'var': 'val'}], indirect=True)
    kwargs = {'env_overrides': None}
    kwargs.update(getattr(request, 'param', {}))

    LOGGER.info("Initializing app...")
    parent = kafka_toolbox.run_app(skip_sync="true", runtime_env_overrides=kwargs['env_overrides'])  # skip sync since it happens before running integration
    sleep(10)  # wait for app to launch
    return parent


@pytest.fixture()
def teardown_app(setup_app):
    LOGGER.info("Terminating app...")
    children = psutil.Process(setup_app)
    for child in children.children(recursive=True):
        child.terminate()
    sleep(10)  # wait for app to fully stop


@pytest.fixture()
def setup_teardown_source_test_data(map_source_input, tmp_path):
    LOGGER.info("Creating source test data input file...")
    with open(tmp_path / 'source_data_in.json', 'w') as f:
        json.dump(map_source_input, f, indent=4, sort_keys=True)


@pytest.fixture()
def setup_teardown_kafka_test_data(map_kafka_input, tmp_path):
    LOGGER.info("Creating kafka test data input file...")
    with open(tmp_path / 'kafka_data_in.json', 'w') as f:
        json.dump(map_kafka_input, f, indent=4, sort_keys=True)
