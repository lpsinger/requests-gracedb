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
    try:
        client = Client('https://gracedb-test.ligo.org/api/', fail_noauth=True)
    except ValueError:
        pytest.skip('no GraceDB credentials found')
    yield client
    client.close()


@pytest.mark.parametrize('labels_in,labels_out', [
    [{'EM_READY', 'DQV'}, ['EM_READY', 'DQV']],
    [['EM_READY', 'DQV'], ['EM_READY', 'DQV']],
    [('EM_READY', 'DQV'), ['EM_READY', 'DQV']],
    ['EM_READY', ['EM_READY']],
    [['EM_READY'], ['EM_READY']],
    [None, []],
    [[], []]
])
def test_events_create(client, socket_enabled, coinc_xml_bytes,
                       labels_in, labels_out):
    result = client.events.create(
        filename='coinc.xml', filecontents=coinc_xml_bytes,
        group='Test', pipeline='gstlal', labels=labels_in)
    assert set(result['labels']) == set(labels_out)


@pytest.fixture
def events_create(client, socket_enabled, coinc_xml_bytes):
    return client.events.create(
        filename='coinc.xml', filecontents=coinc_xml_bytes,
        group='Test', pipeline='gstlal')


def test_events_get(client, events_create):
    event_id = events_create['graceid']
    result = client.events[event_id].get()
    assert events_create == {**result, 'warnings': []}


def test_events_update(client, events_create, coinc_xml_bytes):
    event_id = events_create['graceid']
    client.events.update(
        event_id, filename='coinc.xml',
        filecontents=coinc_xml_bytes + b'<!--foobar-->')


def test_events_search(client, events_create):
    event_id = events_create['graceid']
    result = list(client.events.search(query=event_id))
    assert len(result) == 1
    assert events_create == {**result[0], 'warnings': []}


@pytest.fixture
def labels_create(client, events_create):
    event_id = events_create['graceid']
    return client.events[event_id].labels.create('SKYMAP_READY')


def test_events_labels_create(client, events_create, labels_create):
    event_id = events_create['graceid']
    result = client.events[event_id].labels.get()
    assert result[0]['name'] == 'SKYMAP_READY'


def test_events_labels_delete(client, events_create, labels_create):
    event_id = events_create['graceid']
    client.events[event_id].labels.delete('SKYMAP_READY')
    result = client.events[event_id].labels.get()
    assert len(result) == 0


@pytest.mark.parametrize('filename,filecontents', [
    [None, None],
    ['foo.txt', 'bar']
])
@pytest.mark.parametrize('tags_in,tags_out', [
    [['emfollow', 'p_astro'],
    ['emfollow', 'p_astro']], ['emfollow', ['emfollow']], [None, []]
])
def test_events_logs_create(client, events_create, filename, filecontents,
                            tags_in, tags_out):
    event_id = events_create['graceid']
    result = client.events[event_id].logs.create(
        comment='plugh', filename=filename, filecontents=filecontents,
        tags=tags_in)
    if filename is None:
        assert result['filename'] == ''
    else:
        assert result['filename'] == filename
    assert set(result['tag_names']) == set(tags_out)


def test_events_logs_get(client, events_create):
    event_id = events_create['graceid']
    result = client.events[event_id].logs.get()
    assert result[0]['filename'] == 'coinc.xml'


def test_events_files_get(client, events_create):
    event_id = events_create['graceid']
    result = client.events[event_id].files.get()
    assert 'coinc.xml' in result


def test_events_files_file_get(client, events_create):
    event_id = events_create['graceid']
    client.events[event_id].logs.create(
        comment='plugh', filename='foo.txt', filecontents=b'bar')
    with client.events[event_id].files['foo.txt'].get() as f:
        filecontents = f.read()
    assert filecontents == b'bar'


@pytest.fixture
def events_logs_tags_create(client, events_create):
    event_id = events_create['graceid']
    client.events[event_id].logs[1].tags.create('em_bright')


def test_events_logs_tags_create(client, events_create,
                                 events_logs_tags_create):
    event_id = events_create['graceid']
    result = client.events[event_id].logs[1].tags.get()
    assert result[0]['name'] == 'em_bright'


def test_events_logs_tags_delete(client, events_create,
                                 events_logs_tags_create):
    event_id = events_create['graceid']
    client.events[event_id].logs[1].tags.delete('em_bright')
    result = client.events[event_id].logs[1].tags.get()
    assert len(result) == 0


@pytest.fixture
def superevents_create(client, events_create):
    event_id = events_create['graceid']
    return client.superevents.create(
        preferred_event=event_id, t_0=1e9, t_start=1e9, t_end=1e9)


def test_superevents_create(client, events_create, superevents_create):
    event_id = events_create['graceid']
    assert superevents_create['preferred_event'] == event_id
    assert superevents_create['t_start'] == 1e9
    assert superevents_create['t_0'] == 1e9
    assert superevents_create['t_end'] == 1e9


def test_superevents_update(client, superevents_create):
    superevent_id = superevents_create['superevent_id']
    client.superevents.update(superevent_id, t_start=123, t_0=456, t_end=789)
    result = client.superevents[superevent_id].get()
    assert result['t_start'] == 123
    assert result['t_0'] == 456
    assert result['t_end'] == 789


@pytest.fixture
def events_create_2(client, socket_enabled, coinc_xml_bytes):
    return client.events.create(
        filename='coinc.xml', filecontents=coinc_xml_bytes,
        group='Test', pipeline='gstlal')


@pytest.fixture
def superevents_add(client, superevents_create, events_create_2):
    event_id_2 = events_create_2['graceid']
    superevent_id = superevents_create['superevent_id']
    client.superevents[superevent_id].add(event_id_2)


def test_superevents_add(client, superevents_add, superevents_create,
                         events_create, events_create_2):
    event_id = events_create['graceid']
    event_id_2 = events_create_2['graceid']
    superevent_id = superevents_create['superevent_id']
    result = client.superevents[superevent_id].get()
    assert set(result['gw_events']) == {event_id, event_id_2}


def test_superevents_remove(client, superevents_add, superevents_create,
                            events_create, events_create_2):
    event_id = events_create['graceid']
    event_id_2 = events_create_2['graceid']
    superevent_id = superevents_create['superevent_id']
    client.superevents[superevent_id].remove(event_id_2)
    result = client.superevents[superevent_id].get()
    assert set(result['gw_events']) == {event_id}
