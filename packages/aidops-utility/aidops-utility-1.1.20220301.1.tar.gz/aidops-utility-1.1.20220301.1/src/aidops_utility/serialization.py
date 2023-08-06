import json
from datetime import datetime

class Serialization():

    def serialize(self, obj):

        if isinstance(obj, datetime):
            return obj.__str__()

        if isinstance(obj, object):
            if hasattr(obj, "__dict__"):
                serial = obj.__dict__
                return serial
            else:
                return None

        return obj.__dict__

    def hi(self):
        return 'HI!'

    def object2Json(self, object):
        return json.dumps(object.__dict__, default = self.serialize)