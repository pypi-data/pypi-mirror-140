from django.contrib import admin

from waffle.models import Flag, Switch, Sample


admin.site.unregister(Flag)
admin.site.unregister(Switch)
admin.site.unregister(Sample)