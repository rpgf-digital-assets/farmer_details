from rest_framework import serializers
from api.utils import DynamicFieldsCategorySerializer

from farmer.models import Farmer, FarmerLand
from users.models import User





class FarmerLandCoordinatesSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = FarmerLand
        fields = ('longitude', 'latitude', 'farmer')
        

class UserSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'user_display_name')
        
        
class FarmerDetailsSerializer(DynamicFieldsCategorySerializer):
    user = UserSerializer()
    class Meta:
        model = Farmer
        fields = ('user', 'profile_image')