import msgpack

__virtualname__ = "msgpack"


def dump(hub, data) -> bytes:
    return msgpack.packb(data)


def load(hub, data: bytes):
    return msgpack.unpackb(data, strict_map_key=False)
