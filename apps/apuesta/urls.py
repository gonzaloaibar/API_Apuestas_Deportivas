from rest_framework.routers import DefaultRouter

from .api import PartidoViewSet, ApuestaViewSet,OpcionApuestaViewSet

router = DefaultRouter()
router.register(r'partidos', PartidoViewSet)
router.register(r'apuestas', ApuestaViewSet)
router.register(r'opcion_de_apuestas', OpcionApuestaViewSet)
urlpatterns = router.urls