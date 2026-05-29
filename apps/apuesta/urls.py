from rest_framework.routers import DefaultRouter

from .views import PartidoViewSet, ApuestaViewSet

router = DefaultRouter()
router.register(r'partidos', PartidoViewSet)
router.register(r'apuestas', ApuestaViewSet)
#router.register(r'tipo_apuestas', TipoApuestaViewSet)
urlpatterns = router.urls