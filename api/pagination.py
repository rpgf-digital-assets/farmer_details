from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination 

class LimitOffsetPagination(LimitOffsetPagination):
    page_size = 100
    max_page_size = 1000

class PageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'