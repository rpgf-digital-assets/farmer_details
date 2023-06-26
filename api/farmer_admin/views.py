
from rest_framework.response import Response
from rest_framework.views import APIView

from farmer.models import Farmer
from users.models import User


class DeleteFarmerAPIView(APIView):
    def post(self, request):
        response = {
            'status': '',
            'message': ''
        }
        try:
            farmer_list = request.data['farmers_list']
            print('a jfahkb fa ', type(farmer_list))
            for farmer_pk in request.data['farmers_list']:
                Farmer.objects.get(pk=farmer_pk).delete()
                User.objects.get(pk=farmer_pk).delete()
            response['status'] = 'success'
        except Exception as e:
            response['status'] = 'error'
            response['message'] = str(e)
            
        return Response(response)
    