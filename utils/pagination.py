from utils.exceptions import ValidationError


class PagePagination(object):
    def __init__(self, page_limit, request):
        self.page_limit = page_limit
        self.request = request
        self.page = self._get_page()
        self.next_page = None

    def paginate_query(self, query):
        offset = self.page_limit * (self.page - 1)
        query = query.limit(self.page_limit).offset(offset)
        return query

    async def check_next_page(self, query):
        async with self.request.app['db'].acquire() as conn:
            offset = self.page_limit * self.page
            query = query.limit(1).offset(offset)
            result = await conn.execute(query)

            query_params = ''
            for param, value in self.request.query.items():
                if param != 'page':
                    query_params += '{}={}&'.format(param, value)

            if result.rowcount > 0:
                self.next_page = '{scheme}://{host}{path}?{query}page={page}'\
                                 .format(scheme=self.request.scheme,
                                         host=self.request.host,
                                         path=self.request.path,
                                         query=query_params,
                                         page=self.page + 1)

    def get_paginated_data(self, data):
        response = {
            'next_page': self.next_page,
            'results': data
        }
        return response

    def _get_page(self):
        page = self.request.query.get('page', 1)
        try:
            page = int(page)
        except ValueError:
            raise ValidationError(dict(query_params='Page number is not int'))

        if page < 1:
            raise ValidationError(dict(query_params='Page less that 1 '))
        return page
