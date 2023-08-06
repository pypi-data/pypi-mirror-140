from bson.json_util import dumps
from bson.json_util import loads
from transformHealthEventHubModels.utils import *


class DSEventHubInsertOneObject(object):
    def __init__(self, collection, data):
        self.collection = collection
        self.data = data

    def json(self):
        return {
            "collection": self.collection,
            "data": dumps(self.data, sort_keys=True, default=str)
        }

    @classmethod
    def load_object(cls, json_data):
        data = decodeUTFString(json_data[b'data'])
        return cls(decodeUTFString(json_data[b'collection']), loads(data))
