import json, dataclasses

class BasicSerializer:

    @staticmethod
    def encode_obj(obj):
        if type(obj).__name__ =='instance':
            return obj.__dict__

    @staticmethod
    def serialize(obj):
        return json.dumps(obj, default=BasicSerializer.encode_obj)

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def dataclass_json_dump(obj: object) -> str:
    return json.dumps(obj, cls=EnhancedJSONEncoder)
