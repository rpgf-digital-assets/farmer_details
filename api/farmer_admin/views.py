
from rest_framework.response import Response
from rest_framework.views import APIView


class DeleteFarmerAPIView(APIView):
    def post(self, request):
        print("🐍 File: farmer_admin/views.py | Line: 8 | post ~ request.data",request.data)
        return Response({'status':"success"})