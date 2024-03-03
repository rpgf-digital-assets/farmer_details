
import io

from django.core.files import File
from django.db import connection, transaction
from django.db.models import Avg, Count, F, Func, Sum
from django.db.models.functions import Lower
from django.db.models.functions.comparison import Coalesce
from rest_framework.generics import (DestroyAPIView, ListAPIView,
                                     RetrieveAPIView)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from api.farmer_admin.serializers import (CostsSerializer,
                                          FarmerDetailsSerializer,
                                          FarmerLandCoordinatesSerializer,
                                          GinningSerializer,
                                          SpinningSerializer)
from api.permissions import IsAdminOrSuperUser

from farmer.models import (ContaminationControl, CostOfCultivation, Costs,
                           Farmer, FarmerLand, FarmerOrganicCropPdf,
                           HarvestAndIncomeDetails, NutrientManagement,
                           OrganicCropDetails, OtherFarmer,
                           PestDiseaseManagement, Season, SeedDetails,
                           WeedManagement)
from farmer_admin.utils import generate_certificate
from farmer_details_app.models import (Ginning, GinningStatus,
                                       SelectedGinningFarmer, Spinning,
                                       SpinningStatus, Vendor)
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

class DeleteCostsAPIView(DeleteBaseAPIView):
    model = Costs
    
    
class GetCostsAPIView(APIView):
    
    def post(self, request):
        response = {
            'status': '',
        }
        try:
            data = request.data
            organic_crop_id = data['organic_crop']
            input_source = data['input_source']
            organic_crop = OrganicCropDetails.objects.get(id=organic_crop_id, is_active=True)
            costs = Costs.objects.filter(type=input_source, is_active=True).first()
            nutrient = NutrientManagement.objects.filter(organic_crop=organic_crop, is_active=True).first()
            response['costs'] = CostsSerializer(costs).data
            response['no_of_workdays_required'] = nutrient.no_of_workdays_required if nutrient else 1
            response['status'] = 'success'   
        except Exception as e:
            response['error'] = str(e)
            response['status'] = 'failure'
        return Response(response)
        
        
        
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
        year = request.data.get('year')
        organic_crops = OrganicCropDetails.objects.filter(is_active=True, name=crop_name, year=year)\
        .values('area', 'expected_yield', 'expected_productivity')\
        .aggregate(total_area=Coalesce(Sum('area'), 0.0),
                    total_expected_yield=Coalesce(Sum('expected_yield'), 0.0))
        
        organic_crops['total_area'] = round(organic_crops['total_area'], 3)
        if organic_crops['total_area'] <= 0:
            organic_crops['total_expected_productivity'] = round(organic_crops['total_expected_yield'], 3)
        else:
            organic_crops['total_expected_productivity'] = round(organic_crops['total_expected_yield'] / organic_crops['total_area'], 3)
            

        organic_crop_ids = OrganicCropDetails.objects.filter(is_active=True, name=crop_name, year=year).values_list('id', flat=True)
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
                    SELECT strftime('%Y', fdhf.history_date) AS year, count(fdhf.user_id) AS count from farmer_historicalfarmer as fdhf
                    WHERE fdhf.history_type = '+'
                    GROUP BY year
                """)
                rows = dictfetchall(cursor)
                response['status'] = 'success'
                years_list = [row["year"] for row in rows]
                print("🐍 File: farmer_admin/views.py | Line: 288 | get ~ years_list",years_list)
                counts_list = [row["count"] for row in rows]
                response['data'] = {
                    "years": years_list,
                    "counts": counts_list
                }
                print("🐍 File: farmer_admin/views.py | Line: 711 | get_context_data ~ row", rows)

        except Exception as e:
            response['status'] = 'failure'
            response['message'] = 'Exception Occurred'

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
    
    

class CottonDataAPIView(APIView):
    permission_classes = [HasAPIKey]
    authentication_classes = []
    def get(self, request):
        response = {
            'status': 'success',
            'message': ''
        }
        try:
            data = {}
            
            # Raw cotton data
            total_ginning_added = SelectedGinningFarmer.objects.filter(is_active=True, ginning_mapping__ginning_status__status=GinningStatus.QC_APPROVED)\
                                    .annotate(total_price=F('quantity')*F('price'))\
                                    .aggregate(total_quantity=Sum('quantity'), total_value=Sum('total_price'))
            value_for_one = round(total_ginning_added['total_value'] / total_ginning_added['total_quantity'], 2)
            ginning = Ginning.objects.filter(ginning_status__status=GinningStatus.QC_APPROVED) \
                .aggregate(total_available_quantity=total_ginning_added['total_quantity'] - Sum('ginning_outbound__quantity'), 
                        total_available_value=F('total_available_quantity')*value_for_one)
                
            raw_cotton_district = Ginning.objects.filter(ginning_status__status=GinningStatus.QC_APPROVED) \
                .annotate(ldistrict=Lower('selected_farmers__farmer__district')) \
                .values('ldistrict') \
                .order_by('ldistrict') \
                .annotate(total_available_quantity=Sum('selected_farmers__quantity') - Sum('ginning_outbound__quantity'), 
                            total_available_value=F('total_available_quantity')*value_for_one)
            
            raw_cotton_district_data = {
                "nagpur": {
                    "available": {
                        "quantity": 0,
                        "value": 0
                    }
                },
                "adilabad": {
                    "available": {
                        "quantity": 0,
                        "value": 0
                    }
                },
                "others": {
                    "available": {
                        "quantity": 0,
                        "value": 0
                    }
                }
            }
            
            for raw_cotton in raw_cotton_district:
                if raw_cotton['ldistrict'] == 'nagpur':
                    raw_cotton_district_data['nagpur']['available']['quantity'] = raw_cotton['total_available_quantity']
                    raw_cotton_district_data['nagpur']['available']['value'] = raw_cotton['total_available_value']
                    
                elif raw_cotton['ldistrict'] == 'adilabad':
                    raw_cotton_district_data['adilabad']['available']['quantity'] = raw_cotton['total_available_quantity']
                    raw_cotton_district_data['adilabad']['available']['value'] = raw_cotton['total_available_value']
                    
                else:
                    raw_cotton_district_data['others']['available']['quantity'] += raw_cotton['total_available_quantity']
                    raw_cotton_district_data['others']['available']['value'] += raw_cotton['total_available_value']
                    
                    
                
            data['raw_cotton'] = {
                "available": {
                    "quantity": ginning['total_available_quantity'] or 0,
                    "value": ginning['total_available_value'] or 0,
                },
                "district_based": raw_cotton_district_data
            }
            
            # Lint cotton data
            # Available lint = ginned_outbound - sent for spinning
            spinned_cotton = Spinning.objects.filter(is_active=True, spinning_status__status=SpinningStatus.QC_APPROVED)\
                .aggregate(total_quantity=Sum('spinning_outbound__quantity'))
            ginning_outbound = Ginning.objects.filter(ginning_status__status=GinningStatus.QC_APPROVED) \
                .aggregate(total_ginned_quantity=Sum('ginning_outbound__quantity') - Coalesce(spinned_cotton['total_quantity'], 0.0), 
                        total_ginned_value=F('total_ginned_quantity')*value_for_one)
                
            ginning_district = Ginning.objects.filter(ginning_status__status=GinningStatus.QC_APPROVED) \
                .annotate(ldistrict=Lower('selected_farmers__farmer__district')) \
                .values('ldistrict') \
                .order_by('ldistrict') \
                .annotate(total_ginned_quantity=Func(Coalesce(spinned_cotton['total_quantity'], 0.0) - Sum('ginning_outbound__quantity'), function='ABS'), 
                        total_ginned_value=F('total_ginned_quantity')*value_for_one)
            
            ginned_district_data = {
                "nagpur": {
                    "available": {
                        "quantity": 0,
                        "value": 0
                    }
                },
                "adilabad": {
                    "available": {
                        "quantity": 0,
                        "value": 0
                    }
                },
                "others": {
                    "available": {
                        "quantity": 0,
                        "value": 0
                    }
                }
            }
            
            for ginned_cotton in ginning_district:
                if ginned_cotton['ldistrict'] == 'nagpur':
                    ginned_district_data['nagpur']['available']['quantity'] = ginned_cotton['total_ginned_quantity']
                    ginned_district_data['nagpur']['available']['value'] = ginned_cotton['total_ginned_value']
                    
                elif ginned_cotton['ldistrict'] == 'adilabad':
                    ginned_district_data['adilabad']['available']['quantity'] = ginned_cotton['total_ginned_quantity']
                    ginned_district_data['adilabad']['available']['value'] = ginned_cotton['total_ginned_value']
                    
                else:
                    ginned_district_data['others']['available']['quantity'] += ginned_cotton['total_ginned_quantity']
                    ginned_district_data['others']['available']['value'] += ginned_cotton['total_ginned_value']
                    
            data['lint_cotton'] = {
                "available": {
                    "quantity": ginning_outbound['total_ginned_quantity'] or 0,
                    "value": ginning_outbound['total_ginned_value'] or 0
                },
                "district_based": ginned_district_data
            }
            
            # Yarn data
            # Available Yarn = sent for spinning - spinning_outbound
            data['yarn'] = {
                "available": {
                    "quantity": spinned_cotton['total_quantity'] or 0,
                    "value": (spinned_cotton['total_quantity'] * value_for_one) or 0
                }
            }

            response['data'] = data
            
        except Exception as e:
            response['status'] = 'failure'
            response['message'] = str(e)
            
        return Response(response)
        
        
class YarnAvailableAPIView(APIView):
    permission_classes = [HasAPIKey]
    authentication_classes = []
    
    def get(self, request):
        response = {
            'status': 'success',
            'message': ''
        }
        try:
            
            spinnings = Spinning.objects.annotate(sum_quantity=Sum('selected_ginnings__quantity')).filter(is_active=True, spinning_status__status=SpinningStatus.QC_APPROVED)
            spinnings_json = SpinningSerializer(spinnings, many=True, context={"request": request}).data

            data = {
                'spinnings': spinnings_json
            }
            
            response['data'] = data
            
        except Exception as e:
            response['status'] = 'failure'
            response['message'] = str(e)
            
        return Response(response)
    
    
class YarnTraceabilityAPIView(APIView):
    permission_classes = []
    authentication_classes = []
    
    def get(self, request, **kwargs):
        response = {
            'status': 'success',
            'message': ''
        }
        try:
            spinning = Spinning.objects.annotate(sum_quantity=Sum('selected_ginnings__quantity')).get(id=self.kwargs['pk'])
            ginnings = Ginning.objects.filter(selected_ginnings__in=spinning.selected_ginnings.all())
            farmers = Farmer.objects.filter(ginning_farmer__ginning_mapping__in=ginnings)
            
            data = {
                'spinning': SpinningSerializer(spinning, context={'request':request}).data,
                'ginning': GinningSerializer(ginnings, many=True, context={'request':request}).data,
                'farmers': FarmerDetailsSerializer(farmers, many=True, context={'request':request}).data
            }
            
            response['data'] = data
            
        except Exception as e:
            response['status'] = 'failure'
            response['message'] = str(e)
            
        return Response(response)