from rest_framework.pagination import PageNumberPagination

class PagePagination(PageNumberPagination):
    """
    Custom pagination class to handle the pagination of API responses.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'