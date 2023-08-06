from bson.json_util import dumps
from bson.json_util import loads
from transformHealthEventHubModels.utils import *


class DSEventHubUpdateOneObject(object):
    def __init__(self, collection, filter_condition, operation, upsert=False, array_filters=None):
        self.collection = collection
        self.filter_condition = filter_condition
        self.operation = operation
        self.upsert = upsert
        self.array_filters = array_filters

    def json(self):
        return {
            "collection": self.collection,
            "filter_condition": dumps(self.filter_condition),
            "operation": dumps(self.operation),
            "upsert": str(self.upsert),
            "array_filters": dumps(self.array_filters)
        }

    @classmethod
    def load_object(cls, json_object):
        return cls(
            decodeUTFString(json_object[b"collection"]),
            loads(decodeUTFString(json_object[b"filter_condition"])),
            loads(decodeUTFString(json_object[b"operation"])),
            decodeUTFString(json_object[b"upsert"]),
            loads(decodeUTFString(json_object[b"array_filters"]))
        )
