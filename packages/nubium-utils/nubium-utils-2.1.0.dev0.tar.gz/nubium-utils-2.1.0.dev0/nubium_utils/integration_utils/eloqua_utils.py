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
    with open(tmp_path / 'source_data_in.json', 'r') as f:
        contacts = json.load(f)
        for contact in contacts:
            response = get_eloqua_session().post(url='/api/REST/1.0/data/contact', json=contact)
            response.raise_for_status()
            contact.update({'id': response.json().get('id')})
            contact_id = response.json().get('id')
            contact_ids.append(contact_id)
    yield contact_ids
    LOGGER.info("Deleting contacts from Eloqua...")
    for contact_id in contact_ids:
        response = get_eloqua_session().delete(url=f'/api/REST/1.0/data/contact/{contact_id}')
        response.raise_for_status()


@pytest.fixture()
def contact_field_map():
    response = get_eloqua_session().get('/api/REST/1.0/assets/contact/fields?depth=complete', timeout=30)
    response.raise_for_status()
    return response.json()['elements']


@pytest.fixture()
def create_contact_field_map(contact_field_map):
    return {
        contact_field['internalName']: contact_field['id']
        for contact_field in contact_field_map}


@pytest.fixture()
def retrieved_contact_field_map(contact_field_map):
    result = {contact_field['id']: contact_field['internalName'] for contact_field in contact_field_map}
    return result


def map_retrieved_contact_record(record, retrieved_contact_field_map):
    field_map = {retrieved_contact_field_map[field['id']]: field.get('value', "") for field in record['fieldValues']}
    field_map['C_EmailAddress'] = record.get("emailAddress", "")
    field_map['C_FirstName'] = record.get("firstName", "")
    field_map['C_LastName'] = record.get("lastName", "")
    field_map['C_MobilePhone'] = record.get("mobilePhone", "")
    field_map['C_Country'] = record.get("country", "")
    field_map['C_Address1'] = record.get("address1", "")
    field_map['C_Address2'] = record.get("address2", "")
    field_map['C_Address3'] = record.get("address3", "")
    field_map['C_City'] = record.get("city", "")
    field_map['C_State_Prov'] = record.get("province", "")
    field_map['C_Zip_Postal'] = record.get("postalCode", "")
    field_map['C_Company'] = record.get("accountName", "")
    field_map['C_BusPhone'] = record.get("businessPhone", "")
    field_map['C_Title'] = record.get("title", "")
    field_map['isBounced'] = record.get("isBounceback", "")

    return field_map


@pytest.fixture()
def retrieve_contacts_for_validation(tmp_path, create_delete_contacts, retrieved_contact_field_map):
    contacts = []
    for contact_id in create_delete_contacts:
        response = get_eloqua_session().get(url=f'/api/REST/1.0/data/contact/{contact_id}')
        response.raise_for_status()
        contacts.append(map_retrieved_contact_record(response.json(), retrieved_contact_field_map))
    with open(tmp_path / 'source_data_out.json', 'w') as f:
        json.dump(contacts, f, indent=4, sort_keys=True)
    return contacts
