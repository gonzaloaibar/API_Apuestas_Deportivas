from rest_framework.permissions import BasePermission


class EsAdministrador(BasePermission):

    message = (
        "Solo los administradores pueden realizar esta acción."
    )

    #este metodo se ejecuta automáticamente antes de procesar cualquier petición en la vista
    #este metodo retorna true si permite el acceso o false si lo denega
    def has_permission(self, request, view):
        #busca si el usuario tiene asignado el grupo Administrador
        return request.user.groups.filter(
            name="Administrador"
        ).exists()


class EsCliente(BasePermission):

    message = (
        "Solo los clientes pueden realizar esta acción."
    )

    def has_permission(self, request, view):

        return request.user.groups.filter(
            name="Cliente"
        ).exists()

class EsPropietarioApuesta(BasePermission):

    message = (
        "Solo puede acceder a sus propias apuestas."
    )

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        return obj.apostado_por == request.user