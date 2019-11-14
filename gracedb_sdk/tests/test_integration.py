"""End-to-end tests against a live server."""
import pkgutil
import os

import pytest

from .. import Client


@pytest.fixture
def coinc_xml_bytes():
    return pkgutil.get_data(__name__, os.path.join('data/coinc.xml'))


@pytest.fixture(scope='module')
def client():
    with Client('https://gracedb-test.ligo.org/api/') as client:
        yield client


@pytest.mark.parametrize('labels_in,labels_out', [
    [{'EM_READY', 'DQV'}, ['EM_READY', 'DQV']],
    [['EM_READY', 'DQV'], ['EM_READY', 'DQV']],
    [('EM_READY', 'DQV'), ['EM_READY', 'DQV']],
    ['EM_READY', ['EM_READY']],
    [['EM_READY'], ['EM_READY']],
    [None, []],
    [[], []]
])
def test_labels(client, socket_enabled, coinc_xml_bytes,
                labels_in, labels_out):
    events_create_result = client.events.create(
        filename='coinc.xml', filecontents=coinc_xml_bytes,
        group='Test', pipeline='gstlal', labels=labels_in)
    assert set(events_create_result['labels']) == set(labels_out)


def test_integration(client, socket_enabled, coinc_xml_bytes):
    events_create_result = client.events.create(
        filename='coinc.xml', filecontents=coinc_xml_bytes,
        group='Test', pipeline='gstlal')
    event_id = events_create_result['graceid']

    events_get_result = client.events[event_id].get()
    assert events_create_result == {**events_get_result, 'warnings': []}

    events_logs_result = client.events[event_id].logs.get()
    assert events_logs_result[0]['filename'] == 'coinc.xml'

    events_logs_create_result = client.events[event_id].logs.create(
        comment='testing: 1, 2, 3', tags='emfollow')
    assert events_logs_create_result['comment'] == 'testing: 1, 2, 3'
    assert events_logs_create_result['tag_names'] == ['emfollow']

    client.events[event_id].labels.create('SKYMAP_READY')
    client_event_labels_get_result = client.events[event_id].labels.get()
    assert client_event_labels_get_result[0]['name'] == 'SKYMAP_READY'

    client.events[event_id].labels.delete('SKYMAP_READY')

    events_logs_create_result = client.events[event_id].logs.create(
        comment='foobar', filename='foo.txt', filecontents=b'bar bat')
    assert events_logs_create_result['comment'] == 'foobar'
    assert events_logs_create_result['filename'] == 'foo.txt'

    n = client.events[event_id].logs.get()[-1]['N']
    event_logs_tags_get_result = client.events[event_id].logs[n].tags.get()
    assert event_logs_tags_get_result == []

    events_search_result = list(client.events.search(query=event_id))
    assert len(events_search_result) == 1
    assert events_get_result == events_search_result[0]

    client.events.update(
        event_id, filename='coinc.xml',
        filecontents=coinc_xml_bytes + b'<!--foobar-->')

    superevents_create_result = client.superevents.create(
        preferred_event=event_id, t_0=1e9, t_start=1e9, t_end=1e9)
