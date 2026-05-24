from rest_framework.routers import DefaultRouter

from .api import PartidoViewSet

router = DefaultRouter()
router.register(r'partidos', PartidoViewSet)


urlpatterns = router.urls