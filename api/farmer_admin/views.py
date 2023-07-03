
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from api.farmer_admin.serializers import FarmerDetailsSerializer, FarmerLandCoordinatesSerializer

from farmer.models import Farmer, FarmerLand
from users.models import User


class DeleteFarmerAPIView(APIView):
    def post(self, request):
        response = {
            'status': '',
            'message': ''
        }
        try:
            for farmer_pk in request.data['farmers_list']:
                Farmer.objects.get(pk=farmer_pk).delete()
                User.objects.get(pk=farmer_pk).delete()
            response['status'] = 'success'
        except Exception as e:
            response['status'] = 'error'
            response['message'] = str(e)
            
        return Response(response)
    
class FarmerLandCoordinatesAPIView(ListAPIView):
    serializer_class = FarmerLandCoordinatesSerializer
    queryset = FarmerLand.objects.all()
    

class FarmerDetailsAPIView(RetrieveAPIView):
    serializer_class = FarmerDetailsSerializer
    queryset = Farmer.objects.all()