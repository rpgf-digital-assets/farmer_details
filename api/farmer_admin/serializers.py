from rest_framework import serializers
from api.utils import DynamicFieldsCategorySerializer

from farmer.models import Costs, Farmer, FarmerLand, HarvestAndIncomeDetails, OrganicCropDetails, Season
from farmer_details_app.models import Ginning, SelectedGinning, SelectedGinningFarmer, Spinning, Vendor
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
        

class FarmerOrganicCropDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganicCropDetails
        fields = '__all__'
        

class FarmerDetailsSerializer(DynamicFieldsCategorySerializer):
    user = UserSerializer()
    land = FarmerLandSerializer(many=True)
    organic_crop = FarmerOrganicCropSerializer(many=True)
    class Meta:
        model = Farmer
        fields = ('user', 'profile_image', 'village', 'taluka', 'land', 'organic_crop')
    
    


class CostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Costs
        fields = '__all__'
        
        
        

class VendorSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    class Meta:
        model = Vendor
        fields = ['user_display_name', 'profile_image']

    def get_profile_image(self, instance):
        request = self.context.get('request')
        return str(request.build_absolute_uri(instance.profile_image.url))
        
class SpinningSerializer(serializers.ModelSerializer):
    sum_quantity = serializers.IntegerField()
    lot_combined = serializers.SerializerMethodField()
    vendor = VendorSerializer()
    
    def get_lot_combined(self, instance):
        return "-".join([selected.lot_no for selected in instance.selected_ginnings.all()])
        
    class Meta:
        model = Spinning
        fields = ['id', 'vendor', 'sum_quantity', 'lot_combined', 'timestamp']
        

class SelectedGinningFarmerSerializer(serializers.ModelSerializer):
    farmer = FarmerDetailsSerializer()
    class Meta:
        model = SelectedGinningFarmer   
        fields = '__all__' 
    
    
class GinningSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer()
    selected_farmers = SelectedGinningFarmerSerializer(many=True)
    class Meta:
        model = Ginning
        fields = ['selected_farmers', 'vendor', 'total_quantity', 'timestamp']
    