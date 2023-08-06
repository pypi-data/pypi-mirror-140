import waffle

from .exceptions import ServiceUnavailable


class FlagMixin:
    flags = []

    def dispatch(self, request, *args, **kwargs):
        for flag in self.get_flags():
            if not waffle.switch_is_active(flag):
                raise ServiceUnavailable()
        return super().dispatch(request, *args, **kwargs)
    
    def get_flags(self, *args, **kwargs):
        if self.flags is None:
            self.flags = []
        return self.flags
