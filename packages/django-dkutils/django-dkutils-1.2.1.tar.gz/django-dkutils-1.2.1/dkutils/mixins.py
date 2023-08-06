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
        all_flags = super().get_flags()
        if all_flags is None:
            all_flags = []
        if self.flags is None:
            self.flags = []
        for flag in self.flags:
            if flag not in all_flags:
                all_flags.append(flag)
        return all_flags