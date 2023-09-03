
import io
from django.core.files import File
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from api.farmer_admin.serializers import FarmerDetailsSerializer, FarmerLandCoordinatesSerializer, FarmerOrganicCropDetailsSerializer, FarmerOrganicCropSerializer
from django.db.models import ProtectedError
from django.db.models import Count
from django.db import connection
from django.db import transaction
from django.db.models import Sum, Avg
from api.permissions import IsAdminOrSuperUser
from farmer.models import ContaminationControl, CostOfCultivation, Farmer, FarmerLand, FarmerOrganicCropPdf, HarvestAndIncomeDetails, NutrientManagement, OrganicCropDetails, OtherFarmer, PestDiseaseManagement, Season, SeedDetails, WeedManagement
from farmer_admin.utils import generate_certificate
from farmer_details_app.models import Vendor
from users.models import User
from utils.cursor_fetch import dictfetchall
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
                context = {
                    'crops': organic_crops,
                    'farmer': farmer,
                    'farmer_land': farmer.land.all().first(),
                    "crop_headings": {
                        "seed": SeedDetails._meta.get_fields(),
                        "nutrient": NutrientManagement._meta.get_fields(),
                        "pest": PestDiseaseManagement._meta.get_fields(),
                        "weed": WeedManagement._meta.get_fields(),
                        "harvest": HarvestAndIncomeDetails._meta.get_fields(),
                        "cost": CostOfCultivation._meta.get_fields(),
                        "contamination": ContaminationControl._meta.get_fields(),
                    }
                }
                result = generate_certificate(context=context, request=self.request)
                filename = (f'{farmer.user.user_display_name}_crop.pdf')
                organic_crop_pdf.pdf.save(filename, File(io.BytesIO(result)))
                organic_crop_pdf.save()

            response['status'] = 'success'
            response['pdf_url'] = organic_crop_pdf.pdf.url

        except Exception as e:
            response['status'] = 'exception'
            response['message'] = str(e)

        return Response(response)


class DeleteOtherFarmerAPIView(DeleteBaseAPIView):
    model = OtherFarmer
        


class GetCropNamesAPIView(APIView):
    def get(self, request):
        response = {
            'status': '',
            'code': '',
            'message': ''
        }
        organic_crops = OrganicCropDetails.objects.filter(is_active=True).values('name').annotate(Count("name")).order_by()
        if organic_crops:
            response['status'] = 'success'
            response['data'] = organic_crops
        else:
            response['status'] = 'failure'
            response['message'] = 'No Organic crop found'
            response['code'] = 'no_organic_crop'
        return Response(response)
    

class GetCropDetailsFromNameAPIView(APIView):
    def post(self, request):
        response = {
            'status': '',
            'code': '',
            'message': ''
        }
        crop_name = request.data.get('crop_name')

        organic_crops = OrganicCropDetails.objects.filter(is_active=True, name=crop_name)\
        .values('area', 'expected_yield', 'expected_productivity')\
        .aggregate(total_area=Sum('area'),
                    total_expected_yield=Sum('expected_yield'),
                    total_expected_productivity=Sum('expected_productivity'))

        organic_crop_ids = OrganicCropDetails.objects.filter(is_active=True, name=crop_name).values_list('id', flat=True)
        total_crop_harvested = HarvestAndIncomeDetails.objects.filter(is_active=True, organic_crop__in=organic_crop_ids)\
        .values('first_harvest', 'second_harvest', 'third_harvest', 
                'actual_crop_production', 'quantity_sold_fpo', 'premium_paid_fpo', 
                'quantity_sold_outside', 'premium_paid_outside', 'gross_income')\
        .aggregate(total_first_harvest=Sum('first_harvest'), 
                   total_second_harvest=Sum('second_harvest'), 
                   total_third_harvest=Sum('third_harvest'),
                   total_actual_crop_production=Sum('actual_crop_production'),
                   total_quantity_sold_fpo=Sum('quantity_sold_fpo'),
                   total_premium_paid_fpo=Sum('premium_paid_fpo'),
                   total_quantity_sold_outside=Sum('quantity_sold_outside'),
                   total_premium_paid_outside=Sum('premium_paid_outside'),
                   total_gross_income=Sum('gross_income'))

        total_cost_of_cultivation = CostOfCultivation.objects.filter(is_active=True, organic_crop__in=organic_crop_ids)\
        .values('total_cost') \
        .aggregate(total_cost=Sum('total_cost')) 

        if organic_crops:
            response['status'] = 'success'
            response['data'] = {
                "organic_crop": organic_crops,
                "harvest_details": total_crop_harvested,
                "cost": total_cost_of_cultivation
            }
        else:
            response['status'] = 'failure'
            response['message'] = 'No Organic crop found'
            response['code'] = 'no_organic_crop'
        return Response(response)


class GetarmerLineGraphData(APIView):
    def get(self, request):
        response = {
            'status': '',
            'code': '',
            'message': ''
        }
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT strftime('%m', fdhf.history_date) AS month, count(fdhf.user_id) AS count from farmer_historicalfarmer as fdhf
                    WHERE fdhf.history_type = '+'
                    GROUP BY month
                """)
                rows = dictfetchall(cursor)
                response['status'] = 'success'
                months_list = [row["month"] for row in rows]
                counts_list = [row["count"] for row in rows]
                response['data'] = {
                    "months": months_list,
                    "counts": counts_list
                }
                print("🐍 File: farmer_admin/views.py | Line: 711 | get_context_data ~ row", rows)

        except Exception as e:
            response['status'] = 'failure'
            response['message'] = 'Exception Occured'

        return Response(response)
    
class GetCropBarGraphDetails(APIView):
    def post(self, request):
        response = {
            'status': '',
            'code': '',
            'message': ''
        }
        crop_name = request.data.get('crop_name')
        organic_crop_ids = OrganicCropDetails.objects.filter(is_active=True, name=crop_name).values_list('id', flat=True)
        costs = CostOfCultivation.objects.filter(is_active=True, organic_crop__in=organic_crop_ids) \
        .aggregate(total_input_cost=Sum('input_cost'), total_seed_purchase_cost=Sum('seed_purchase_cost'),
                   total_irrigation_cost=Sum('irrigation_cost'), total_machinery_cost=Sum('machinery_cost'),
                   total_animal_labour_cost=Sum('animal_labour_cost'), total_labour_hiring_cost=Sum('total_labour_hiring_cost'),
                   total_harvest_labour_cost=Sum('harvest_labour_cost'), total_cost=Sum('total_cost'),)
        average_costs = CostOfCultivation.objects.filter(is_active=True, organic_crop__in=organic_crop_ids) \
        .aggregate(total_input_cost=Avg('input_cost'), total_seed_purchase_cost=Avg('seed_purchase_cost'),
                   total_irrigation_cost=Avg('irrigation_cost'), total_machinery_cost=Avg('machinery_cost'),
                   total_animal_labour_cost=Avg('animal_labour_cost'), total_labour_hiring_cost=Avg('total_labour_hiring_cost'),
                   total_harvest_labour_cost=Avg('harvest_labour_cost'), total_cost=Avg('total_cost'))
        response['status'] = 'success'
        cost_keys = [
            "Cost of input preparation",
            "Cost of Seed",
            "Irrigation cost",
            "Hired labour charges (Machinery)",
            "Hired labour charges (Animal)",
            "Hired labour charges (Human)",
            "Cost of Harvesting",
            "Total cost",
        ]
        response['data'] = {
            "x_axis": cost_keys,
            "y_axis": list(costs.values()),
            "average_costs": list(average_costs.values()),
        }
        return Response(response)