from rest_framework import routers

from .views import SwitchViewSet


router = routers.DefaultRouter()
router.register(r'', SwitchViewSet)

urlpatterns = router.urls
