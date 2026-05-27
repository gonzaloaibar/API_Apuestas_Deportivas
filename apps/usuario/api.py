from rest_framework.response import Response
from rest_framework.views import APIView
from apps.usuario.serializers import UsuarioSerializer
from rest_framework import status

class RegistroUsuarioAPIView(APIView):
    
    def post(self,request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()

            return Response({"menasje":f"El usuario: { serializer.data["username"]} fue registrado exitosamente"},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)

