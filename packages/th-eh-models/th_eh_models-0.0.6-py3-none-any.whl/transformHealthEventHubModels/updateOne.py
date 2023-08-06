import json


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
            "filter_condition": json.dumps(self.filter_condition),
            "operation": json.dumps(self.operation),
            "upsert": str(self.upsert),
            "array_filters": json.dumps(self.array_filters)
        }
