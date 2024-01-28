from django.conf import settings
from django.db import transaction

from farmer.models import ContaminationControl, CostOfCultivation, Farmer, FarmerEducation, FarmerLand, FarmerSocial, HarvestAndIncomeDetails, NutrientManagement, OrganicCropDetails, PestDiseaseManagement, Season, SeedDetails, WeedManagement
from users.models import User


def create_farmer(row):
    try:
        row_dict = row.to_dict()
        phone = f"+91{row_dict['phone']}"
        # user = User.objects.filter(is_active=True, phone=phone).first()
        # if user:
        #     return "User already exists with the same phone number"
        user, _created = User.objects.get_or_create(phone=phone, 
                                                    defaults={"role": User.FARMER, 
                                                              "first_name": row_dict['first_name'], 
                                                              "last_name": row_dict['last_name'], })
        user.set_password(settings.DEFAULT_PASSWORD)
        user.save()
        del row_dict['first_name']
        del row_dict['last_name']
        del row_dict['phone']
        farmer, _created = Farmer.objects.get_or_create(user=user, defaults=row_dict)
        return farmer
    except Exception as e:
        return str(e)


def create_farmer_social(row, instance_df):
    try:
        index = row.name
        row_dict = row.to_dict()
        farmer = instance_df.loc[index, 'FARMER_HEADERS']
        # Check if instance is farmer instance then proceed to check social validations
        if isinstance(farmer, Farmer):
            non_empty_row = any(row_dict.values())
            if non_empty_row:
                with transaction.atomic():
                    farmer_education, _created = FarmerEducation.objects.get_or_create(
                        name__iexact=row_dict['education'])
                    del row_dict['education']
                    farmer_social, _created = FarmerSocial.objects.get_or_create(
                        farmer=farmer,education=farmer_education, defaults=row_dict)
                    return farmer_social
            else:
                return None
        return farmer
    except Exception as e:
        return str(e)


def create_farmer_land(row, instance_df):
    try:
        index = row.name
        row_dict = row.to_dict()
        farmer = instance_df.loc[index, 'FARMER_HEADERS']
        # Check if instance is farmer instance then proceed to check social validations
        if isinstance(farmer, Farmer):
            non_empty_row = any(row_dict.values())
            if non_empty_row:
                row_dict['last_conducted'] = None if row_dict['last_conducted'] == '' else row_dict['last_conducted']
                farmer_land, _created = FarmerLand.objects.get_or_create(farmer=farmer, defaults=row_dict)
                return farmer_land
            else:
                return None
        return farmer
    except Exception as e:
        return str(e)


def create_farmer_organic_crop(row, instance_df):
    try:
        index = row.name
        row_dict = row.to_dict()
        farmer = instance_df.loc[index, 'FARMER_HEADERS']
        # farmer_land = instance_df.loc[index, 'FARMER_LAND_HEADERS']
        
        # Check if instance is farmer instance then proceed to check social validation
        if isinstance(farmer, Farmer):
            non_empty_row = any(row_dict.values())
            if non_empty_row:
                farmer_land = FarmerLand.objects.filter(is_active=True, farmer=farmer).first()
                if farmer_land:
                    organic_crops = OrganicCropDetails.objects.filter(is_active=True, farmer=farmer)
                    total_organic_crop_area = sum([item.area for item in organic_crops])
                    if int(farmer_land.total_organic_land) < int(total_organic_crop_area + row_dict['area']):
                        return "Farmer land area is less than the organic crop area"
                    else:
                        # Create season
                        season = Season.objects.filter(name__iexact=row_dict['season']).first()
                        if not season:
                            return "Season not found"
                        del row_dict['season']
                        # Create a new Organic Crop
                        organic_crop, _created = OrganicCropDetails.objects.get_or_create(is_active=True, farmer=farmer, season=season, defaults=row_dict)
                        return organic_crop
                else:
                    return "Farmer land not found"
            else:
                return None
        return farmer
    except Exception as e:
        return str(e)


def create_farmer_organic_seed(row, instance_df):
    try:
        index = row.name
        row_dict = row.to_dict()
        organic_crop = instance_df.loc[index, 'ORGANIC_CROP_HEADERS']
        if isinstance(organic_crop, OrganicCropDetails):
            non_empty_row = any(row_dict.values())
            if non_empty_row:
                seed_details = SeedDetails.objects.get_or_create(organic_crop=organic_crop, **row_dict)
                return seed_details
            else: 
                return None
        return organic_crop
    except Exception as e:
        return str(e)


def create_farmer_organic_nutrient(row, instance_df):
    try:
        index = row.name
        row_dict = row.to_dict()
        organic_crop = instance_df.loc[index, 'ORGANIC_CROP_HEADERS']
        if isinstance(organic_crop, OrganicCropDetails):
            non_empty_row = any(row_dict.values())
            if non_empty_row:
                row_dict['type'] = row_dict.pop('nutrient_type')
                nutrient = NutrientManagement.objects.get_or_create(organic_crop=organic_crop, **row_dict)
                return nutrient
            else: 
                return None
        return organic_crop
    except Exception as e:
        return str(e)


def create_farmer_organic_pest_disease(row, instance_df):
    try:
        index = row.name
        row_dict = row.to_dict()
        organic_crop = instance_df.loc[index, 'ORGANIC_CROP_HEADERS']
        if isinstance(organic_crop, OrganicCropDetails):
            non_empty_row = any(row_dict.values())
            if non_empty_row:
                pest_disease = PestDiseaseManagement.objects.get_or_create(organic_crop=organic_crop, **row_dict)
                return pest_disease
            else: 
                return None
        return organic_crop
    except Exception as e:
        return str(e)


def create_farmer_organic_weed(row, instance_df):
    try:
        index = row.name
        row_dict = row.to_dict()
        organic_crop = instance_df.loc[index, 'ORGANIC_CROP_HEADERS']
        if isinstance(organic_crop, OrganicCropDetails):
            non_empty_row = any(row_dict.values())
            if non_empty_row:
                weed = WeedManagement.objects.get_or_create(organic_crop=organic_crop, **row_dict)
                return weed
            else: 
                return None
        return organic_crop
    except Exception as e:
        return str(e)


def create_farmer_organic_harvest(row, instance_df):
    try:
        index = row.name
        row_dict = row.to_dict()
        organic_crop = instance_df.loc[index, 'ORGANIC_CROP_HEADERS']
        if isinstance(organic_crop, OrganicCropDetails):
            non_empty_row = any(row_dict.values())
            if non_empty_row:
                row_dict['type'] = row_dict.pop('harvest_type')
                harvest = HarvestAndIncomeDetails.objects.get_or_create(organic_crop=organic_crop, **row_dict)
                return harvest
            else: 
                return None
        return organic_crop
    except Exception as e:
        return str(e)


def create_farmer_organic_cost(row, instance_df):
    try:
        index = row.name
        row_dict = row.to_dict()
        organic_crop = instance_df.loc[index, 'ORGANIC_CROP_HEADERS']
        if isinstance(organic_crop, OrganicCropDetails):
            non_empty_row = any(row_dict.values())
            if non_empty_row:
                cost = CostOfCultivation.objects.get_or_create(organic_crop=organic_crop, **row_dict)
                return cost
            else: 
                return None
        return organic_crop
    except Exception as e:
        return str(e)


def create_farmer_organic_contamination(row, instance_df):
    try:
        index = row.name
        row_dict = row.to_dict()
        organic_crop = instance_df.loc[index, 'ORGANIC_CROP_HEADERS']
        if isinstance(organic_crop, OrganicCropDetails):
            non_empty_row = any(row_dict.values())
            if non_empty_row:
                contamination = ContaminationControl.objects.get_or_create(organic_crop=organic_crop, **row_dict)
                return contamination
            else: 
                return None
        return organic_crop
    except Exception as e:
        return str(e)
