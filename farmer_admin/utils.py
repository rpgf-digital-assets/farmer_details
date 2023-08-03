from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML, CSS


country_list = [
    ("Afghanistan", "Afghanistan"),
    ("Åland Islands", "Åland Islands"),
    ("Albania", "Albania"),
    ("Algeria", "Algeria"),
    ("American Samoa", "American Samoa"),
    ("Andorra", "Andorra"),
    ("Angola", "Angola"),
    ("Anguilla", "Anguilla"),
    ("Antarctica", "Antarctica"),
    ("Antigua and Barbuda", "Antigua and Barbuda"),
    ("Argentina", "Argentina"),
    ("Armenia", "Armenia"),
    ("Aruba", "Aruba"),
    ("Australia", "Australia"),
    ("Austria", "Austria"),
    ("Azerbaijan", "Azerbaijan"),

    ("Bahamas", "Bahamas"),
    ("Bahrain", "Bahrain"),
    ("Bangladesh", "Bangladesh"),
    ("Barbados", "Barbados"),
    ("Belarus", "Belarus"),
    ("Belgium", "Belgium"),
    ("Belize", "Belize"),
    ("Benin", "Benin"),
    ("Bermuda", "Bermuda"),
    ("Bhutan", "Bhutan"),
    ("Bolivia", "Bolivia"),
    ("Bosnia and Herzegovina", "Bosnia and Herzegovina"),
    ("Botswana", "Botswana"),
    ("Bouvet Island", "Bouvet Island"),
    ("Brazil", "Brazil"),
    ("British Indian Ocean Territory", "British Indian Ocean Territory"),
    ("Brunei Darussalam", "Brunei Darussalam"),
    ("Bulgaria", "Bulgaria"),
    ("Burkina Faso", "Burkina Faso"),
    ("Burundi", "Burundi"),

    ("Cambodia", "Cambodia"),
    ("Cameroon", "Cameroon"),
    ("Canada", "Canada"),
    ("Cape Verde", "Cape Verde"),
    ("Cayman Islands", "Cayman Islands"),
    ("Central African Republic", "Central African Republic"),
    ("Chad", "Chad"),
    ("Chile", "Chile"),
    ("China", "China"),
    ("Christmas Island", "Christmas Island"),
    ("Cocos (Keeling) Islands", "Cocos (Keeling) Islands"),
    ("Colombia", "Colombia"),
    ("Comoros", "Comoros"),
    ("Congo, Republic of (Brazzaville)", "Congo, Republic of (Brazzaville)"),
    ("Democratic Republic of the Congo (Kinshasa)",
     "Democratic Republic of the Congo (Kinshasa)"),
    ("Cook Islands", "Cook Islands"),
    ("Costa Rica", "Costa Rica"),
    ("Cote D'ivoire (Ivory Coast)", "Cote D'ivoire (Ivory Coast)"),
    ("Croatia", "Croatia"),
    ("Cuba", "Cuba"),
    ("Cyprus", "Cyprus"),
    ("Czech Republic", "Czech Republic"),

    ("Denmark", "Denmark"),
    ("Djibouti", "Djibouti"),
    ("Dominica", "Dominica"),
    ("Dominican Republic", "Dominican Republic"),

    ("Ecuador", "Ecuador"),
    ("Egypt", "Egypt"),
    ("El Salvador", "El Salvador"),
    ("Equatorial Guinea", "Equatorial Guinea"),
    ("Eritrea", "Eritrea"),
    ("Estonia", "Estonia"),
    ("Ethiopia", "Ethiopia"),

    ("Falkland Islands (Malvinas)", "Falkland Islands (Malvinas)"),
    ("Faroe Islands", "Faroe Islands"),
    ("Fiji", "Fiji"),
    ("Finland", "Finland"),
    ("France", "France"),
    ("French Guiana", "French Guiana"),
    ("French Polynesia", "French Polynesia"),
    ("French Southern Territories", "French Southern Territories"),

    ("Gabon", "Gabon"),
    ("The Gambia", "The Gambia"),
    ("Georgia", "Georgia"),
    ("Germany", "Germany"),
    ("Ghana", "Ghana"),
    ("Gibraltar", "Gibraltar"),
    ("Greece", "Greece"),
    ("Greenland", "Greenland"),
    ("Grenada", "Grenada"),
    ("Guadeloupe", "Guadeloupe"),
    ("Guam", "Guam"),
    ("Guatemala", "Guatemala"),
    ("Guernsey", "Guernsey"),
    ("Guinea", "Guinea"),
    ("Guinea-Bissau", "Guinea-Bissau"),
    ("Guyana", "Guyana"),

    ("Haiti", "Haiti"),
    ("Heard Island and Mcdonald Islands", "Heard Island and Mcdonald Islands"),
    ("Holy See (Vatican City State)", "Holy See (Vatican City State)"),
    ("Honduras", "Honduras"),
    ("Hong Kong", "Hong Kong"),
    ("Hungary", "Hungary"),

    ("Iceland", "Iceland"),
    ("India", "India"),
    ("Indonesia", "Indonesia"),
    ("Iran, Islamic Republic Of", "Iran, Islamic Republic Of"),
    ("Iraq", "Iraq"),
    ("Ireland", "Ireland"),
    ("Isle of Man", "Isle of Man"),
    ("Israel", "Israel"),
    ("Italy", "Italy"),
    ("Ivory Coast", "Ivory Coast"),

    ("Jamaica", "Jamaica"),
    ("Japan", "Japan"),
    ("Jersey", "Jersey"),
    ("Jordan", "Jordan"),

    ("Kazakhstan", "Kazakhstan"),
    ("Kenya", "Kenya"),
    ("Kiribati", "Kiribati"),
    ("Korea, Democratic People's Republic of",
     "Korea, Democratic People's Republic of"),
    ("Korea, Republic of", "Korea, Republic of"),
    ("Kuwait", "Kuwait"),
    ("Kyrgyzstan", "Kyrgyzstan"),

    ("Lao, People's Democratic Republic", "Lao, People's Democratic Republic"),
    ("Latvia", "Latvia"),
    ("Lebanon", "Lebanon"),
    ("Lesotho", "Lesotho"),
    ("Liberia", "Liberia"),
    ("Libya", "Libya"),
    ("Liechtenstein", "Liechtenstein"),
    ("Lithuania", "Lithuania"),
    ("Luxembourg", "Luxembourg"),

    ("Macao", "Macao"),
    ("Madagascar", "Madagascar"),
    ("Malawi", "Malawi"),
    ("Malaysia", "Malaysia"),
    ("Maldives", "Maldives"),
    ("Mali", "Mali"),
    ("Malta", "Malta"),
    ("Marshall Islands", "Marshall Islands"),
    ("Martinique", "Martinique"),
    ("Mauritania", "Mauritania"),
    ("Mauritius", "Mauritius"),
    ("Mayotte", "Mayotte"),
    ("Mexico", "Mexico"),
    ("Micronesia, Federated States of", "Micronesia, Federated States of"),
    ("Moldova, Republic of", "Moldova, Republic of"),
    ("Monaco", "Monaco"),
    ("Mongolia", "Mongolia"),
    ("Montenegro", "Montenegro"),
    ("Montserrat", "Montserrat"),
    ("Morocco", "Morocco"),
    ("Mozambique", "Mozambique"),
    ("Myanmar (Burma)", "Myanmar (Burma)"),

    ("Namibia", "Namibia"),
    ("Nauru", "Nauru"),
    ("Nepal", "Nepal"),
    ("Netherlands", "Netherlands"),
    ("Netherlands Antilles", "Netherlands Antilles"),
    ("New Caledonia", "New Caledonia"),
    ("New Zealand", "New Zealand"),
    ("Nicaragua", "Nicaragua"),
    ("Niger", "Niger"),
    ("Nigeria", "Nigeria"),
    ("Niue", "Niue"),
    ("Norfolk Island", "Norfolk Island"),
    ("Northern Macedonia, The Former Yugoslav Republic of",
     "Northern Macedonia, The Former Yugoslav Republic of"),
    ("Northern Mariana Islands", "Northern Mariana Islands"),
    ("Norway", "Norway"),

    ("Oman", "Oman"),

    ("Pakistan", "Pakistan"),
    ("Palau", "Palau"),
    ("Palestinian Territory, Occupied", "Palestinian Territory, Occupied"),
    ("Panama", "Panama"),
    ("Papua New Guinea", "Papua New Guinea"),
    ("Paraguay", "Paraguay"),
    ("Peru", "Peru"),
    ("Philippines", "Philippines"),
    ("Pitcairn Island", "Pitcairn Island"),
    ("Poland", "Poland"),
    ("Portugal", "Portugal"),
    ("Puerto Rico", "Puerto Rico"),

    ("Qatar", "Qatar"),

    ("Reunion Island", "Reunion Island"),
    ("Romania", "Romania"),
    ("Russian Federation", "Russian Federation"),
    ("Rwanda", "Rwanda"),

    ("Saint Helena", "Saint Helena"),
    ("Saint Kitts and Nevis", "Saint Kitts and Nevis"),
    ("Saint Lucia", "Saint Lucia"),
    ("Saint Pierre and Miquelon", "Saint Pierre and Miquelon"),
    ("Saint Vincent and the Grenadines", "Saint Vincent and the Grenadines"),
    ("Samoa", "Samoa"),
    ("San Marino", "San Marino"),
    ("Sao Tome and Principe", "Sao Tome and Principe"),
    ("Saudi Arabia", "Saudi Arabia"),
    ("Senegal", "Senegal"),
    ("Serbia", "Serbia"),
    ("Seychelles", "Seychelles"),
    ("Sierra Leone", "Sierra Leone"),
    ("Singapore", "Singapore"),
    ("Slovakia (Slovak Republic)", "Slovakia (Slovak Republic)"),
    ("Slovenia", "Slovenia"),
    ("Solomon Islands", "Solomon Islands"),
    ("Somalia", "Somalia"),
    ("South Africa", "South Africa"),
    ("South Georgia and the South Sandwich Islands",
     "South Georgia and the South Sandwich Islands"),
    ("South Sudan", "South Sudan"),
    ("Spain", "Spain"),
    ("Sri Lanka", "Sri Lanka"),
    ("Sudan", "Sudan"),
    ("Suriname", "Suriname"),
    ("Svalbard and Jan Mayen", "Svalbard and Jan Mayen"),
    ("Swaziland (Eswatini)", "Swaziland (Eswatini)"),
    ("Sweden", "Sweden"),
    ("Switzerland", "Switzerland"),
    ("Syrian Arab Republic", "Syrian Arab Republic"),

    ("Taiwan, Province of China", "Taiwan, Province of China"),
    ("Tajikistan", "Tajikistan"),
    ("Tanzania, United Republic of", "Tanzania, United Republic of"),
    ("Thailand", "Thailand"),
    ("Timor-Leste (East Timor)", "Timor-Leste (East Timor)"),
    ("Togo", "Togo"),
    ("Tokelau", "Tokelau"),
    ("Tonga", "Tonga"),
    ("Trinidad and Tobago", "Trinidad and Tobago"),
    ("Tunisia", "Tunisia"),
    ("Turkey", "Turkey"),
    ("Turkmenistan", "Turkmenistan"),
    ("Turks and Caicos Islands", "Turks and Caicos Islands"),
    ("Tuvalu", "Tuvalu"),

    ("Uganda", "Uganda"),
    ("Ukraine", "Ukraine"),
    ("United Arab Emirates (UAE)", "United Arab Emirates (UAE)"),
    ("United Kingdom (UK)", "United Kingdom (UK)"),
    ("United States (US)", "United States (US)"),
    ("United States Minor Outlying Islands",
     "United States Minor Outlying Islands"),
    ("Uruguay", "Uruguay"),
    ("Uzbekistan", "Uzbekistan"),

    ("Vanuatu", "Vanuatu"),
    ("Venezuela", "Venezuela"),
    ("Vietnam", "Vietnam"),
    ("Virgin Islands, British", "Virgin Islands, British"),
    ("Virgin Islands, U.S.", "Virgin Islands, U.S."),

    ("Wallis and Futuna", "Wallis and Futuna"),
    ("Western Sahara", "Western Sahara"),

    ("Yemen", "Yemen"),

    ("Zambia", "Zambia"),
    ("Zimbabwe", "Zimbabwe")
]


page_width = "297mm"  # Width of the page in millimeters
page_height = "210mm" # Height of the page in millimeters


def generate_certificate(context, request):
    template_name = 'farmer_admin/organic_crop_pdf.html'
    html_string = render_to_string(template_name,
                                context=context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    return html.write_pdf()


def get_model_field_names(model, ignore_fields=['content_object']):
    '''
    ::param model is a Django model class
    ::param ignore_fields is a list of field names to ignore by default
    This method gets all model field names (as strings) and returns a list 
    of them ignoring the ones we know don't work (like the 'content_object' field)
    '''
    model_fields = model._meta.get_fields()
    model_field_names = list(set([f.name for f in model_fields if f.name not in ignore_fields]))
    return model_field_names


def get_lookup_fields(model, fields=None):
    '''
    ::param model is a Django model class
    ::param fields is a list of field name strings.
    This method compares the lookups we want vs the lookups
    that are available. It ignores the unavailable fields we passed.
    '''
    model_field_names = get_model_field_names(model)
    if fields is not None:
        '''
        we'll iterate through all the passed field_names
        and verify they are valid by only including the valid ones
        '''
        lookup_fields = []
        for x in fields:
            if "__" in x:
                # the __ is for ForeignKey lookups
                lookup_fields.append(x)
            elif x in model_field_names:
                lookup_fields.append(x)
    else:
        '''
        No field names were passed, use the default model fields
        '''
        lookup_fields = model_field_names
    return lookup_fields

def qs_to_dataset(qs, fields=None):
    '''
    ::param qs is any Django queryset
    ::param fields is a list of field name strings, ignoring non-model field names
    This method is the final step, simply calling the fields we formed on the queryset
    and turning it into a list of dictionaries with key/value pairs.
    '''

    lookup_fields = get_lookup_fields(qs.model, fields=fields)
    return list(qs.values(*lookup_fields))
