import datetime
from pandas._libs import Timestamp

def base_validations(field_name, field_value, validator, validation_value):
    if validator == 'max_length':
        assert len(str(
            field_value)) <= validation_value, f"{field_name} Length should be less than or equal to {validation_value}"
    elif validator == 'null':
        if not validation_value:
            assert field_value != '', f"{field_name} cannot be null"


def base_validator(field, value):
    # Send to other validation methods
    for validator, validation_value in field['validators'].items():
        base_validations(field['name'], value, validator, validation_value)


def charfield_validator(field, value):
    # Check if the value is only valid characters
    pass


def booleanfield_validator(field, value):
    assert value == True or value == False, f"{field['name']} value must be True or False"


def datefield_validator(field, value):
    if value != '':
        if not isinstance(value, Timestamp):
            raise ValueError(f"{field['name']} incorrect data format, should be YYYY-MM-DD")
    

def datetimefield_validator(field, value):
    if value != '':
        if not isinstance(value, Timestamp):
            raise ValueError(f"{field['name']} incorrect data format, should be YYYY-MM-DD")
    # try:
    #     datetime.date.fromisoformat(value)
    # except ValueError:
    #     raise ValueError(f"{field['name']} has incorrect data format, should be YYYY-MM-DD")


def foreignkey_validator(field, value):
    pass


def floatfield_validator(field, value):
    if value != '':
        try:
            assert float(value) >= 0.0, f"{field['name']} cannot be negative"
        except ValueError:
            f"{field['name']} must be a number"

def integerfield_validator(field, value):
    if value != '':
        try:        
            assert int(value) >= 0, f"{field['name']} cannot be negative"
        except ValueError:
            f"{field['name']} must be a number"


def positive_integer_validator(field, value):
    if value != '':
        try:
            assert int(value) >= 0, f"{field['name']} cannot be negative"
        except ValueError:
            f"{field['name']} must be a positive number"

def imagefield_validator(field, value):
    pass

def filefield_validator(field, value):
    pass

FIELDS_VALIDATION_MAPPING = {
    'BooleanField': booleanfield_validator,
    'CharField': charfield_validator,
    'DateField': datefield_validator,
    'DateTimeField': datetimefield_validator,
    'ForeignKey':  foreignkey_validator,
    'FloatField': floatfield_validator,
    'IntegerField': integerfield_validator,
    'PositiveIntegerField': positive_integer_validator,
    'ImageField': imagefield_validator,
    'FileField': filefield_validator,
}

def validate_fields(field, value):
    try:
        base_validator(field, value)
        FIELDS_VALIDATION_MAPPING[field['type']](field, value)
    except Exception as e:
        return str(e)
    return None
