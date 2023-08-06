from rest_framework import routers

from .views import SwitchViewSet


router = routers.DefaultRouter()
router.register(r'switches', SwitchViewSet)

urlpatterns = router.urls
