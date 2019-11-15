from .base import Resource


VOEVENT_TYPES = {'preliminary': 'PR',
                 'retraction': 'RE',
                 'update': 'UP',
                 'initial': 'IN'}


# FIXME: events have a 'event/' resource whereas superevents have 'events/'.
# Combine BaseVOEvents, EventVOEvents, and SupereventVOEvents into a single
# VOEvents class once this inconsistency has been fixed.
class BaseVOEvents(Resource):

    def create_or_update(self, key, *, voevent_type=None, coinc_comment=None,
                         **kwargs):
        data = {'voevent_type': VOEVENT_TYPES[voevent_type],
                # FIXME: why doesn't GraceDB have a default for this field?
                'CoincComment': coinc_comment or False,
                **kwargs}
        return super().create_or_update(key, data=data)

    def get(self, **kwargs):
        return super().get(**kwargs)['voevents']


class EventVOEvents(BaseVOEvents):

    path = 'voevent/'


class SupereventVOEvents(BaseVOEvents):

    path = 'voevents/'
