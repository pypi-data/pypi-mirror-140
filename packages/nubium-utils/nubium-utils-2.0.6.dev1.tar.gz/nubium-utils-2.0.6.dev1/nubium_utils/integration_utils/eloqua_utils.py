import json
import logging
from os import environ

import pytest
from python_eloqua_wrapper import EloquaSession

LOGGER = logging.getLogger(__name__)


def get_eloqua_session():
    return EloquaSession(
        username=environ['ELOQUA_USER'],
        password=environ['ELOQUA_PASSWORD'],
        company=environ['ELOQUA_COMPANY'])


@pytest.fixture()
def create_delete_contacts(tmp_path):
    LOGGER.info("Creating contacts in Eloqua...")
    contact_ids = []
    with open(tmp_path / 'test_data_in.json', 'r') as f:
        contacts = json.load(f)
        for contact in contacts:
            response = get_eloqua_session().post(url='/api/REST/1.0/data/contact', json=contact)
            response.raise_for_status()
            contact.update({'id': response.json().get('id')})
            contact_id = response.json().get('id')
            contact_ids.append(contact_id)
    yield None
    LOGGER.info("Deleting contacts from Eloqua...")
    for contact_id in contact_ids:
        response = get_eloqua_session().delete(url=f'/api/REST/1.0/data/contact/{contact_id}')
        response.raise_for_status()


@pytest.fixture()
def create_contact_field_map():
    response = get_eloqua_session().get('/api/REST/1.0/assets/contact/fields?depth=complete', timeout=30)
    response.raise_for_status()
    contact_fields = response.json()['elements']
    return {
        contact_field['internalName']: contact_field['id']
        for contact_field in contact_fields}
