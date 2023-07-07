from rest_framework import serializers
from api.utils import DynamicFieldsCategorySerializer

from farmer.models import Farmer, FarmerLand, OrganicCropDetails
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
        
class FarmerOrganicCropSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = OrganicCropDetails
        fields = ('name', 'area')
        
        
class FarmerDetailsSerializer(DynamicFieldsCategorySerializer):
    user = UserSerializer()
    land = FarmerLandSerializer(many=True)
    organic_crop = FarmerOrganicCropSerializer(many=True)
    class Meta:
        model = Farmer
        fields = ('user', 'profile_image', 'village', 'taluka', 'land', 'organic_crop')
    
    # def get_land(self, obj):
    #     return obj.land.all().first()
        