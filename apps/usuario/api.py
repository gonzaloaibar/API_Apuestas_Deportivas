from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView
from apps.usuario.models import Usuario
from apps.usuario.serializers import UsuarioSerializer
from rest_framework import status
from decimal import Decimal



class RegistroUsuarioAPIView(APIView):
    
    def post(self,request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()

            return Response({"menasje":f"El usuario: { serializer.data["username"]} fue registrado exitosamente"},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)

class TraerUsuariosAPIView(APIView):
    def get(self,request):
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios,many=True)
        return Response(serializer.data)


#Voy a crear un endpoint cpn una accion especifica para cargar saldo
#la peticion sera un POST, porque no PATCH porque PATCH reemplazaria el saldo actual
#con el saldo que quiere cargar el usuario, por lo tanto no es una actualizacion es una
#agregacion.
class CargarSaldoAPIView(APIView):

    def post(self,request,pk=None):
        usuario = Usuario.objects.get(pk=pk)

        monto = request.data["monto"]

        if monto < 0:
            return Response({'error':'El monto ingresado no es valido'},status=HTTP_400_BAD_REQUEST)

        usuario.saldo += Decimal(str(monto)) #convierto el saldo a Decimal
        usuario.save()
        return Response({"Saldo actual":usuario.saldo},status=HTTP_200_OK)
