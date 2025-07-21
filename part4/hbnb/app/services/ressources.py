from uuid import UUID


def is_valid_uuid4(uuid_str):
    """Determines if given str is a uuid4"""
    try:
        val = UUID(uuid_str, version=4)
        return val.version == 4
    except ValueError:
        return False
