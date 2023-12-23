
from farmer.models import ContaminationControl, CostOfCultivation, Farmer, FarmerEducation, FarmerLand, FarmerSocial, HarvestAndIncomeDetails, NutrientManagement, OrganicCropDetails, PestDiseaseManagement, SeedDetails, WeedManagement
from users.models import User


def get_formatted_field(field):
    formatted_field = {
        'name': field.name,
        'type': field.get_internal_type(),
        'validators': {
            'null': field.blank and field.null
        }
    }
    for validator in field.validators:
        try:
            formatted_field['validators'][validator.code] = validator.limit_value
        except Exception as e:
            pass
    return formatted_field


def get_headers(model, exclude_list=[], include_list=None):
    default_exclude_list = ['id', 'is_active']
    formatted_fields = {}
    for field in model._meta.get_fields():
        if include_list:
            if field.name in include_list:
                formatted_fields[field.name] = get_formatted_field(field)
                continue
        else:
            if field.name in exclude_list + default_exclude_list:
                continue
            else:
                formatted_fields[field.name] = get_formatted_field(field)
    return formatted_fields


USER_HEADERS_LIST = ['first_name', 'last_name', 'phone']
USER_HEADERS = get_headers(User, include_list=USER_HEADERS_LIST)
FARMER_HEADERS_LIST = ['phone', 'gender', 'birth_date', 'aadhar_number', 'registration_number',
                       'date_of_joining_of_program', 'village', 'taluka', 'district', 'state', 'country']
FARMER_HEADERS = get_headers(Farmer, include_list=FARMER_HEADERS_LIST)
FARMER_HEADERS.update(USER_HEADERS)

FARMER_SOCIAL_HEADERS = get_headers(FarmerSocial, exclude_list=['farmer'])

FARMER_LAND_HEADERS = get_headers(FarmerLand, exclude_list=['farmer'])

ORGANIC_CROP_HEADERS_LIST = ['name', 'type', 'area', 'date_of_sowing', 'expected_date_of_harvesting',
                             'expected_yield', 'expected_productivity', 'season', 'year']
ORGANIC_CROP_HEADERS = get_headers(
    OrganicCropDetails, include_list=ORGANIC_CROP_HEADERS_LIST)

SEED_DETAILS_HEADERS = get_headers(SeedDetails, exclude_list=['organic_crop'])

NUTRIENT_HEADERS = get_headers(NutrientManagement, exclude_list=['organic_crop'])
type = NUTRIENT_HEADERS['type']
NUTRIENT_HEADERS['nutrient_type'] = type
del NUTRIENT_HEADERS['type']

PEST_DISEASE_HEADERS = get_headers(PestDiseaseManagement, exclude_list=['organic_crop'])
WEED_HEADERS = get_headers(WeedManagement, exclude_list=['organic_crop'])

HARVEST_HEADERS = get_headers(HarvestAndIncomeDetails, exclude_list=['organic_crop'])
type = HARVEST_HEADERS['type']
HARVEST_HEADERS['harvest_type'] = type
del HARVEST_HEADERS['type']

COST_HEADERS = get_headers(CostOfCultivation, exclude_list=['organic_crop'])
CONTAMINATION_HEADERS = get_headers(ContaminationControl, exclude_list=['organic_crop'])

HEADER_LIST = {
    'FARMER_HEADERS': FARMER_HEADERS,
    'FARMER_SOCIAL_HEADERS': FARMER_SOCIAL_HEADERS,
    'FARMER_LAND_HEADERS': FARMER_LAND_HEADERS,
    'ORGANIC_CROP_HEADERS': ORGANIC_CROP_HEADERS,
    'SEED_DETAILS_HEADERS': SEED_DETAILS_HEADERS,
    'NUTRIENT_HEADERS': NUTRIENT_HEADERS,
    'PEST_DISEASE_HEADERS': PEST_DISEASE_HEADERS,
    'WEED_HEADERS': WEED_HEADERS,
    'HARVEST_HEADERS': HARVEST_HEADERS,
    'COST_HEADERS': COST_HEADERS,
    'CONTAMINATION_HEADERS': CONTAMINATION_HEADERS,
}

CAN_BE_NULL_HEADER_LIST = ['FARMER_SOCIAL_HEADERS', 'FARMER_LAND_HEADERS','SEED_DETAILS_HEADERS',
                           'NUTRIENT_HEADERS', 'PEST_DISEASE_HEADERS', 'WEED_HEADERS', 'HARVEST_HEADERS', 
                           'COST_HEADERS', 'CONTAMINATION_HEADERS',]