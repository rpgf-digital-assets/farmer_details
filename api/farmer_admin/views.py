
import io
from django.core.files import File
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from api.farmer_admin.serializers import FarmerDetailsSerializer, FarmerLandCoordinatesSerializer
from django.db.models import ProtectedError
from django.db import transaction
from api.permissions import IsAdminOrSuperUser
from farmer.models import ContaminationControl, CostOfCultivation, Farmer, FarmerLand, FarmerOrganicCropPdf, HarvestAndIncomeDetails, NutrientManagement, OrganicCropDetails, PestDiseaseManagement, Season, SeedDetails, WeedManagement
from farmer_admin.utils import generate_certificate
from farmer_details_app.models import Vendor
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
    
    
class DeleteOrganicCropAPIView(APIView):
    def post(self, request):
        response = {
            'status': '',
            'code': '',
            'message': ''
        }
        data = request.data
        model_type_mapping = {
            "seed": SeedDetails,
            "nutrient": NutrientManagement,
            'pest_disease': PestDiseaseManagement,
            "weed": WeedManagement,
            "harvest_income": HarvestAndIncomeDetails,
            "cost_of_cultivation": CostOfCultivation,
            "contamination_control": ContaminationControl
        }
        with transaction.atomic():
            try:
                type = data['type']
                pk = data['pk']
                if type == 'organic_crop':
                    organic_crop = OrganicCropDetails.objects.get(id=pk)
                    for object in organic_crop.seed.all():
                        object.is_active = False
                        object.save()
                    for object in organic_crop.nutrient.all():
                        object.is_active = False
                        object.save()
                    for object in organic_crop.pest_disease.all():
                        object.is_active = False
                        object.save()
                    for object in organic_crop.weed.all():
                        object.is_active = False
                        object.save()
                    for object in organic_crop.harvest_income.all():
                        object.is_active = False
                        object.save()
                    for object in organic_crop.cost_of_cultivation.all():
                        object.is_active = False
                        object.save()
                    for object in organic_crop.contamination_control.all():
                        object.is_active = False
                        object.save()

                    organic_crop.is_active = False
                    organic_crop.save()
                else:
                    object = model_type_mapping[type].objects.get(id=pk)
                    object.is_active = False
                    object.save()
                response['status'] = 'success'

            except Exception as e:
                response['status'] = 'exception'
                response['message'] = str(e)

        return Response(response)
    
    
class FarmerOrganicCropGeneratePDFAPIView(APIView):
    def get(self, request, pk):
        response = {
            'status': '',
            'code': '',
            'message': ''
        }
        try:
            farmer = Farmer.objects.get(user__id=pk)
            organic_crop_pdf = FarmerOrganicCropPdf.objects.create(farmer=farmer)
            # if _created:
            organic_crops = OrganicCropDetails.objects.filter(farmer=farmer, is_active=True)
            if organic_crops:
                result = generate_certificate({'crops': organic_crops}, request=self.request)
                filename = (f'{farmer.user.user_display_name}_crop.pdf')
                organic_crop_pdf.pdf.save(filename, File(io.BytesIO(result)))
                organic_crop_pdf.save()

            response['status'] = 'success'
            response['pdf_url'] = organic_crop_pdf.pdf.url

        except Exception as e:
            response['status'] = 'exception'
            response['message'] = str(e)

        return Response(response)

            

        