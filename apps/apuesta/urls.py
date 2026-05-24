from rest_framework.routers import DefaultRouter

from .views import PartidoViewSet

router = DefaultRouter()
router.register(r'partidos', PartidoViewSet)


urlpatterns = router.urls