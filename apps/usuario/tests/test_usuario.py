from .fixture_usuario import *
from ...apuesta.api import resolver_apuesta_perdida

@pytest.mark.django_db
def test_superuser(crear_superuser):
    super_usuario = crear_superuser

    assert super_usuario.is_staff == True
    assert super_usuario.is_active == True
    assert super_usuario.username == 'admin'