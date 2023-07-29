from rest_framework import serializers
from api.utils import DynamicFieldsCategorySerializer

from farmer.models import Farmer, FarmerLand, HarvestAndIncomeDetails, OrganicCropDetails, Season
from users.models import User





class FarmerLandCoordinatesSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = FarmerLand
        fields = ('longitude', 'latitude', 'farmer')
        

class UserSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'user_display_name')
        
class FarmerLandSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = FarmerLand
        fields = ('image', )
        

class SeasonSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = Season
        fields = ('name', )

class HarvestAndIncomeDetailsSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = HarvestAndIncomeDetails
        fields = ('gross_income', 'total_crop_harvested', )

class FarmerOrganicCropSerializer(DynamicFieldsCategorySerializer):
    season = SeasonSerializer()
    harvest_income = HarvestAndIncomeDetailsSerializer(many=True)
    class Meta:
        model = OrganicCropDetails
        fields = ('name', 'type', 'area', 'expected_yield', 'expected_date_of_harvesting', 'season', 'harvest_income')
        
        

class FarmerDetailsSerializer(DynamicFieldsCategorySerializer):
    user = UserSerializer()
    land = FarmerLandSerializer(many=True)
    organic_crop = FarmerOrganicCropSerializer(many=True)
    class Meta:
        model = Farmer
        fields = ('user', 'profile_image', 'village', 'taluka', 'land', 'organic_crop')
    
    


        