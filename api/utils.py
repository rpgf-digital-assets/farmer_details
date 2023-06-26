from elasticsearch_dsl import Q as ESQ
from elasticsearch_dsl.connections import get_connection
from nutrify.middleware import CustomLogging


def get_suggestions_list(request, index_document):
    context = []
    get_params = request.GET
    get_params_dict = dict(get_params)

    cleaned_get_params = {}
    for parameter, value in get_params_dict.items():
        blank_value = True
        for val in value:
            if val != '':
                blank_value = False
        if not blank_value:
            if parameter in ('search_results_datatable_length', 'csrfmiddlewaretoken'):
                continue
            cleaned_get_params[parameter] = value
    search_query = get_params_dict.get('q', None)
    es = get_connection()

    index_name = index_document._default_index()
    raw_data = es.indices.get_mapping(index_name)
    schema = raw_data[index_name]["mappings"]["properties"]

    # only get fields with type 'completion'
    completion_type_fields = []
    for field, value in schema.items():
        try:
            if schema[field]['type'] == 'completion':
                completion_type_fields.append(field)
        except:
            CustomLogging.process_exception(None, request, None)
            pass

    # phrase suggestion did you mean functionality
    suggest_dict = {
        "suggest": {
            "text": str(search_query)
        }
    }

    for field in completion_type_fields:
        key = f'{field}_phrase'
        suggest_dict['suggest'][key] = {
            "phrase": {
                "field": f"{field}.trigram",
                "size": 1,
                "gram_size": 3,
                "direct_generator": [
                    {
                        "field": f"{field}.trigram",
                        "suggest_mode": "always"
                    }
                ],
                "highlight": {
                    "pre_tag": "<strong>",
                    "post_tag": "</strong>"
                }
            }
        }
    # phrase suggester format
    # suggest_dict = {
    #     "suggest": {
    #         "text": "benzened",
    #         "ingredient_phrase": {
    #             "phrase": {
    #                 "field": "ingredient.trigram",
    #                 "size": 1,
    #                 "gram_size": 3,
    #                 "direct_generator": [
    #                     {
    #                         "field": "ingredient.trigram",
    #                         "suggest_mode": "always"
    #                     }
    #                 ],
    #                 "highlight": {
    #                     "pre_tag": "<em>",
    #                     "post_tag": "</em>"
    #                 }
    #             }
    #         },
    #         "coa_phrase": {
    #             "phrase": {
    #                 "field": "coa.trigram",
    #                 "size": 1,
    #                 "gram_size": 3,
    #                 "direct_generator": [
    #                     {
    #                         "field": "coa.trigram",
    #                         "suggest_mode": "always"
    #                     }
    #                 ],
    #                 "highlight": {
    #                     "pre_tag": "<em>",
    #                     "post_tag": "</em>"
    #                 }
    #             }
    #         }
    #     }
    # }
    if search_query is not None:
        suggest_dict_response = es.search(
            index=index_name, body=suggest_dict)
        list_suggest_dict_response = list(
            suggest_dict_response['suggest'].keys())
        suggestion_list = []
        for suggestion in list_suggest_dict_response:
            options = suggest_dict_response['suggest'][suggestion][0]['options']
            if len(options) > 0:
                for option in options:
                    if option['highlighted'] not in suggestion_list:
                        suggestion_list.append(option['highlighted'])
        if len(suggestion_list) > 0:
            context = list(suggestion_list)

    try:
        del cleaned_get_params['q']
        del cleaned_get_params['page']
    except:
        CustomLogging.process_exception(None, request, None)
        pass

    return context
