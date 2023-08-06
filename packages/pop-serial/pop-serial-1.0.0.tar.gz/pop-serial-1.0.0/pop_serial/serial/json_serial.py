import json

__virtualname__ = "json"


def _default(data):
    if isinstance(data, set):
        return sorted(data)
    elif hasattr(data, "__iter__"):
        return list(data)
    else:
        return repr(data)


def dump(hub, data) -> bytes:
    return json.dumps(data, default=_default, allow_nan=True, cls=None).encode()


def load(hub, data: bytes):
    return json.loads(data.decode())
