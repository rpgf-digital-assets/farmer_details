
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from api.farmer_admin.serializers import FarmerDetailsSerializer, FarmerLandCoordinatesSerializer
from django.db.models import ProtectedError
from django.db import transaction
from api.permissions import IsAdminOrSuperUser
from farmer.models import Farmer, FarmerLand
from farmer_details_app.models import Season, Vendor
from users.models import User

class DeleteBaseAPIView(DestroyAPIView):
    permission_classes = [IsAdminOrSuperUser]
    model = None
    
    def __init__(self, *args, **kwargs):
        if self.model is None:
            raise AttributeError("You must provide a model attribute")
        return super(DeleteBaseAPIView, self).__init__(*args, **kwargs)
    
    def post(self, request):
        response = {
            'status': '',
            'message': ''
        }
        try:
            with transaction.atomic():
                for pk in request.data['object_pk_list']:
                    object = self.model.objects.get(pk=pk)
                    object.is_active=False
                    object.save()
                        
            response['status'] = 'success'
        except Exception as e:
            response['status'] = 'error'
            response['message'] = str(e)
            
        return Response(response)


class DeleteFarmerAPIView(DeleteBaseAPIView):
    model = User
    
    
class FarmerLandCoordinatesAPIView(ListAPIView):
    serializer_class = FarmerLandCoordinatesSerializer
    queryset = FarmerLand.objects.all()
    

class FarmerDetailsAPIView(RetrieveAPIView):
    serializer_class = FarmerDetailsSerializer
    queryset = Farmer.objects.all()
    
    
class DeleteVendorAPIView(DeleteBaseAPIView):
    model = Vendor
    
class DeleteSeasonAPIView(DeleteBaseAPIView):
    model = Season
    
    
    
    