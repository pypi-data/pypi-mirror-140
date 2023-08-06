import json

try:
    import orjson
except ImportError:
    ORJSON_S = False
else:
    ORJSON_S = True


if ORJSON_S:
    def _to_json(data: dict):
        return orjson.dumps(data).decode('utf-8')
else:
    def _to_json(data: dict):
        return json.dumps(data, ensure_ascii=True)