import waffle


def resolve(name):
    return waffle.switch_is_active(name)
