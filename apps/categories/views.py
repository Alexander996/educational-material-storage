from aiohttp import web
from aiohttp.web_exceptions import HTTPMethodNotAllowed

from apps.categories.models import Category
from apps.categories.serializers import CategorySerializer
from project.permissions import IsTeacherOrAbove
from utils import views
from utils.exceptions import ValidationError
from utils.permissions import IsAuthenticated

category_routes = web.RouteTableDef()


@category_routes.view('/api/categories/')
class CategoriesView(views.ListView):
    model = Category
    serializer_class = CategorySerializer
    pagination_class = None

    @staticmethod
    def get_permission_classes(request):
        if request.method == 'POST':
            return [IsTeacherOrAbove]
        else:
            return [IsAuthenticated]


@category_routes.view(r'/api/categories/{pk:\d+}/')
class CategoryView(views.DetailView):
    model = Category
    serializer_class = CategorySerializer

    @staticmethod
    def get_permission_classes(request):
        if request.method == 'GET':
            return [IsAuthenticated]
        else:
            return [IsTeacherOrAbove]

    async def delete(self):
        raise HTTPMethodNotAllowed


@category_routes.get('/api/categories/search/')
async def search_categories(request):
    async with request.app['db'].acquire() as conn:
        text = request.query.get('text')
        if text is None:
            raise ValidationError(dict(text='This query parameters is required'))

        query = Category.select().where(Category.c.name.like('%{}%'.format(text)))
        result = await conn.execute(query)

        serializer = CategorySerializer(many=True)
        data = await serializer.to_json(result)
        return web.json_response(data)
