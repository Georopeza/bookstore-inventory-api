from rest_framework.routers import SimpleRouter

from .views import BookViewSet

router = SimpleRouter()
# El enunciado documenta las rutas sin barra final; el sufijo opcional acepta
# ambas formas para no romper a un cliente que la añada.
router.trailing_slash = "/?"
router.register("books", BookViewSet, basename="book")

urlpatterns = router.urls
