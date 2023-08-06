from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param, remove_query_param


class NormalResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_next_url(self):
        if not self.page.has_next():
            return None
        url = self.request.get_full_path()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_url(self):
        if not self.page.has_previous():
            return None
        url = self.request.get_full_path()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)

    def get_paginated_response(self, data):
        if not self.page.has_next():
            next_page = None
        else:
            next_page = self.page.next_page_number()
        return Response({
            'next_url': self.get_next_url(),
            'previous_url': self.get_previous_url(),
            'next_link': self.get_next_link(),
            'previous_link': self.get_previous_link(),
            'next_page': next_page,
            'current_length': len(data),
            'total_count': self.page.paginator.count,
            'page_num': self.page.number,
            'num_pages': self.page.paginator.num_pages,
            'page_size': self.page.paginator.per_page,
            'data': data,
            'message': 'ok',
            'code': 200
        })


class LargeNormalResultsSetPagination(NormalResultsSetPagination):
    page_size = 20


class AiitPagination(NormalResultsSetPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            data={
                'data': data,
                'page': {
                    'currentPage': self.page.number,
                    'totalPage': self.page.paginator.num_pages,
                    'pageSize': self.page.paginator.per_page,
                    'totalSize': self.page.paginator.count,
                    'hasNext': self.page.has_next(),
                    'hasPrevious': self.page.has_previous()
                },
                'message': 'ok',
                'code': 200
            })


class LargeAiitPagination(AiitPagination):
    page_size = 20
