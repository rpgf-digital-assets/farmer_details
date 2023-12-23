import csv
import os
import pandas as pd
import sib_api_v3_sdk

from sib_api_v3_sdk.rest import ApiException

from django.forms import ValidationError

from celery import shared_task

from django import db
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db import transaction
from django.template.loader import render_to_string

from farmer_details_app.models import ApplicationConfiguration, BulkUpload

from .formatted_fields import CAN_BE_NULL_HEADER_LIST, HEADER_LIST
from .upload import *
from .validation import validate_fields

file_path = settings.BULK_UPLOAD_FILE_PATH
error_path = settings.BULK_UPLOAD_ERROR_PATH


configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = settings.BREVO_API_KEY
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
sender = {
    "name": "Farmer Portal",
    "email": settings.BREVO_SENDER_EMAIL
}

def get_recipients():
    application_config = ApplicationConfiguration.objects.filter(
        name='BulkUploadEmailList').first()
    
    if application_config:
        email_to = application_config.value
    else:
        email_to = 'vivek@rpgf.com'
        
    email_to = email_to.split(sep=';')
    to = [{"email": email} for email in email_to]
    
    return to

def send_failure_email(bulk_upload):
    subject = 'Farmer Bulk Upload Failure'
    
    to = get_recipients()
    
    params = {
        "timestamp": bulk_upload.timestamp.strftime("%Y-%m-%d %H:%M")
    }
    attachment = {
        'url': bulk_upload.error_document.url
    }
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, 
                                                    sender=sender, 
                                                    template_id=2, 
                                                    subject=subject, 
                                                    params=params, 
                                                    attachment=[attachment]
                                                    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)


def send_success_email(bulk_upload):
    subject = 'Farmer Bulk Upload Success'
    
    to = get_recipients()
    
    params = {
        "timestamp": bulk_upload.timestamp.strftime("%Y-%m-%d %H:%M")
    }
    attachment = {
        'url': bulk_upload.upload_document.url
    }
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, 
                                                    sender=sender, 
                                                    template_id=1, 
                                                    subject=subject, 
                                                    params=params, 
                                                    attachment=[attachment]
                                                    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
    

def validate_row(row, header_name):
    # Converting to numpy array because of Pandas series accessing by index warning
    row_dict = row.to_dict()
    # object_row = {
    #     'field_name': 'Value entered by user in csv',
    #     ...
    # }
    validation_error_list = []
    if header_name in CAN_BE_NULL_HEADER_LIST:
        empty_row = not any(row_dict.values())
        if empty_row:
            return validation_error_list
    for key, value in row_dict.items():
        field = HEADER_LIST[header_name][key]
        # field = {'type': "CharField", "validators": {"max_length": 1, "null": False}}
        validation_error = validate_fields(field, value)
        if validation_error:
            validation_error_list.append(validation_error)
    return validation_error_list


@shared_task
def validate_bulk_upload(bulk_upload_pk):
    bulk_upload = BulkUpload.objects.get(pk=bulk_upload_pk)
    
    if settings.FARMER_ENVIRONMENT == 'DEV':
        url = bulk_upload.upload_document.path
    elif settings.FARMER_ENVIRONMENT == 'PROD':
        url = bulk_upload.upload_document.url
        
    excel_data = pd.read_excel(url).fillna('')
    
    is_valid = True
    with open(f'{error_path}errors.csv', mode='w', newline='') as out_file:
        csv_writer = csv.writer(out_file)
        instance_df = pd.DataFrame(index=range(len(excel_data))).fillna('')
        db.connections.close_all()

        # Field level validation
        error_df = pd.DataFrame()
        for header_name, header in HEADER_LIST.items():
            df = pd.DataFrame(excel_data, columns=header.keys()).fillna('')
            validation_errors = df.apply(lambda row: validate_row(
                row, header_name), axis=1)  # Returns a pandas series
            for index, validation_error in validation_errors.items():
                df.loc[index, f'{header_name}_errors'] = ''
                if validation_error:
                    is_valid = False
                    df.loc[index, f'{header_name}_errors'] = ', '.join(
                        validation_error)
            error_df = pd.concat([error_df, df], axis=1)

        # Adding to Database along with validation
        if is_valid:
            try:
                with transaction.atomic():
                    # Add farmer
                    df = pd.DataFrame(
                        excel_data, columns=HEADER_LIST['FARMER_HEADERS'].keys()).fillna('')
                    instances = df.apply(lambda row: create_farmer(
                        row), axis=1)  # Returns a pandas series
                    for index, instance in instances.items():
                        if isinstance(instance, str):
                            is_valid = False
                            error_df.loc[index,
                                        'FARMER_HEADERS_errors'] = f"{error_df.loc[index, 'FARMER_HEADERS_errors']}, {instance}"
                        else:
                            instance_df.loc[index, 'FARMER_HEADERS'] = instance

                    if is_valid:
                        # Add farmer social
                        df = pd.DataFrame(excel_data, columns=HEADER_LIST['FARMER_SOCIAL_HEADERS'].keys()).fillna('')
                        instances = df.apply(lambda row: create_farmer_social(
                            row, instance_df), axis=1)  # Returns a pandas series
                        for index, instance in instances.items():
                            if isinstance(instance, str):
                                is_valid = False
                                error_df.loc[index,'FARMER_SOCIAL_HEADERS_errors'] = f"{error_df.loc[index, 'FARMER_SOCIAL_HEADERS_errors']}, {instance}"
                            else:
                                pass
                                # instance_df.loc[index,'FARMER_SOCIAL_HEADERS'] = instance

                        # Add farmer land
                        df = pd.DataFrame(excel_data, columns=HEADER_LIST['FARMER_LAND_HEADERS'].keys()).fillna('')
                        instances = df.apply(lambda row: create_farmer_land(
                            row, instance_df), axis=1)  # Returns a pandas series
                        for index, instance in instances.items():
                            if isinstance(instance, str):
                                is_valid = False
                                error_df.loc[index,'FARMER_LAND_HEADERS_errors'] = f"{error_df.loc[index, 'FARMER_LAND_HEADERS_errors']}, {instance}"
                            else:
                                pass
                                # instance_df.loc[index, 'FARMER_LAND_HEADERS'] = instance
                        
                        # Add farmer organic crop
                        df = pd.DataFrame(excel_data, columns=HEADER_LIST['ORGANIC_CROP_HEADERS'].keys()).fillna('')
                        instances = df.apply(lambda row: create_farmer_organic_crop(row, instance_df), axis=1)  # Returns a pandas 
                        for index, instance in instances.items():
                            if isinstance(instance, str):
                                is_valid = False
                                error_df.loc[index,'ORGANIC_CROP_HEADERS_errors'] = f"{error_df.loc[index, 'ORGANIC_CROP_HEADERS_errors']}, {instance}"
                            else:
                                instance_df.loc[index, 'ORGANIC_CROP_HEADERS'] = instance
                            
                        if is_valid:
                            # Organic Crop was successfully completed.
                            # Proceed to add organic crop details
                            # Add Seed details
                            df = pd.DataFrame(excel_data, columns=HEADER_LIST['SEED_DETAILS_HEADERS'].keys()).fillna('')
                            print("🐍 File: farmer_admin/tasks.py | Line: 173 | validate_bulk_upload ~ error_df 1",error_df)
                            
                            instances = df.apply(lambda row: create_farmer_organic_seed(row, instance_df), axis=1)  # Returns a pandas 
                            print("🐍 File: farmer_admin/tasks.py | Line: 219 | validate_bulk_upload ~ instances",instances)
                            
                            for index, instance in instances.items():
                                if isinstance(instance, str):
                                    is_valid = False
                                    error_df.loc[index,'SEED_DETAILS_HEADERS_errors'] = f"{error_df.loc[index, 'SEED_DETAILS_HEADERS_errors']}, {instance}"
                                else:
                                    pass
                                    # instance_df.loc[index, 'SEED_DETAILS_HEADERS'] = 'instance'
                                    
                            
                            # Add nutrient details
                            df = pd.DataFrame(excel_data, columns=HEADER_LIST['NUTRIENT_HEADERS'].keys()).fillna('')
                            instances = df.apply(lambda row: create_farmer_organic_nutrient(row, instance_df), axis=1)  # Returns a pandas 
                            for index, instance in instances.items():
                                if isinstance(instance, str):
                                    is_valid = False
                                    error_df.loc[index,'NUTRIENT_HEADERS_errors'] = f"{error_df.loc[index, 'NUTRIENT_HEADERS_errors']}, {instance}"
                                else:
                                    pass
                                    # instance_df.loc[index, 'NUTRIENT_HEADERS'] = instance
                            
                            # Add Pest disease
                            df = pd.DataFrame(excel_data, columns=HEADER_LIST['PEST_DISEASE_HEADERS'].keys()).fillna('')
                            instances = df.apply(lambda row: create_farmer_organic_pest_disease(row, instance_df), axis=1)  # Returns a pandas 
                            for index, instance in instances.items():
                                if isinstance(instance, str):
                                    is_valid = False
                                    error_df.loc[index,'PEST_DISEASE_HEADERS_errors'] = f"{error_df.loc[index, 'PEST_DISEASE_HEADERS_errors']}, {instance}"
                                else:
                                    pass
                                    # instance_df.loc[index, 'PEST_DISEASE_HEADERS'] = instance
                            
                            # Add Weed
                            df = pd.DataFrame(excel_data, columns=HEADER_LIST['WEED_HEADERS'].keys()).fillna('')
                            instances = df.apply(lambda row: create_farmer_organic_weed(row, instance_df), axis=1)  # Returns a pandas 
                            for index, instance in instances.items():
                                if isinstance(instance, str):
                                    is_valid = False
                                    error_df.loc[index,'WEED_HEADERS_errors'] = f"{error_df.loc[index, 'WEED_HEADERS_errors']}, {instance}"
                                else:
                                    pass
                                    # instance_df.loc[index, 'WEED_HEADERS'] = instance
                            
                            # Add Harvest
                            df = pd.DataFrame(excel_data, columns=HEADER_LIST['HARVEST_HEADERS'].keys()).fillna('')
                            instances = df.apply(lambda row: create_farmer_organic_harvest(row, instance_df), axis=1)  # Returns a pandas 
                            for index, instance in instances.items():
                                if isinstance(instance, str):
                                    is_valid = False
                                    error_df.loc[index,'HARVEST_HEADERS_errors'] = f"{error_df.loc[index, 'HARVEST_HEADERS_errors']}, {instance}"
                                else:
                                    pass
                                    # instance_df.loc[index, 'HARVEST_HEADERS'] = instance
                            
                            # Add Cost
                            df = pd.DataFrame(excel_data, columns=HEADER_LIST['COST_HEADERS'].keys()).fillna('')
                            instances = df.apply(lambda row: create_farmer_organic_cost(row, instance_df), axis=1)  # Returns a pandas 
                            for index, instance in instances.items():
                                if isinstance(instance, str):
                                    is_valid = False
                                    error_df.loc[index,'COST_HEADERS_errors'] = f"{error_df.loc[index, 'COST_HEADERS_errors']}, {instance}"
                                else:
                                    pass
                                    # instance_df.loc[index, 'COST_HEADERS'] = instance
                            
                            # Add Contamination
                            df = pd.DataFrame(excel_data, columns=HEADER_LIST['CONTAMINATION_HEADERS'].keys()).fillna('')
                            instances = df.apply(lambda row: create_farmer_organic_contamination(row, instance_df), axis=1)  # Returns a pandas 
                            for index, instance in instances.items():
                                if isinstance(instance, str):
                                    is_valid = False
                                    error_df.loc[index,'CONTAMINATION_HEADERS_errors'] = f"{error_df.loc[index, 'CONTAMINATION_HEADERS_errors']}, {instance}"
                                else:
                                    pass
                                    # instance_df.loc[index, 'CONTAMINATION_HEADERS'] = instance
                  
                    if not is_valid:
                        raise ValidationError("Something is wrong")
            except Exception as e:
                db.connections.close_all()
                is_valid = False
                print("🐍 File: farmer_admin/tasks.py | Line: 289 | validate_bulk_upload ~ e",e)
                transaction.rollback()
                
        
        if not is_valid:
            csv_writer.writerow(error_df.columns)
            for row in error_df.values:
                csv_writer.writerow(row)
        
        out_file.close()

    if is_valid:
        # If there is no error send success email
        # Change status of bulk upload to success
        bulk_upload.status = BulkUpload.SUCCESS
        send_success_email(bulk_upload)
    else:
        error_file = open(f'{error_path}errors.csv', "rb")
        django_file = File(error_file)
        bulk_upload.error_document.save('errors.csv', django_file)
        bulk_upload.status = BulkUpload.ERROR
        error_file.close()

        # # Send email with error attachment.
        send_failure_email(bulk_upload)
    
    bulk_upload.save()
    db.connections.close_all()
    os.remove(f'{error_path}errors.csv')

    return "Completed task successfully"
