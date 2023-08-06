import waffle

from .exceptions import ServiceUnavailable


def resolve(name, raise_exception=True):
    is_active = waffle.switch_is_active(name)
    if not is_active and raise_exception:
        raise ServiceUnavailable()
    return is_active
