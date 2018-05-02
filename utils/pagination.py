from utils.exceptions import ValidationError


class PagePagination(object):
    def __init__(self, page_limit, request):
        self.page_limit = page_limit
        self.page = self._get_page(request)

    def paginate_query(self, query):
        offset = self.page_limit * (self.page - 1)
        query = query.limit(self.page_limit).offset(offset)
        return query

    def _get_page(self, request):
        page = request.query.get('page', 1)
        try:
            page = int(page)
        except ValueError:
            raise ValidationError(dict(query_params='Page number is not int'))

        if page < 1:
            raise ValidationError(dict(query_params='Page less that 1 '))
        return page
