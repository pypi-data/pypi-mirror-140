import json


class DSEventHubInsertOneObject(object):
    def __init__(self, collection, data):
        self.collection = collection
        self.data = data

    def json(self):
        return {
            "collection": self.collection,
            "data": json.dumps(self.data) if isinstance(self.data, dict) else self.data
        }
