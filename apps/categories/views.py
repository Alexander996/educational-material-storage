from aiohttp import web

from apps.categories.models import Category
from apps.categories.serializers import CategorySerializer
from utils import views

category_routes = web.RouteTableDef()


@category_routes.view('/api/categories/')
class CategoriesView(views.ListView):
    model = Category
    serializer_class = CategorySerializer


@category_routes.view(r'/api/categories/{pk:\d+}/')
class CategoryView(views.DetailView):
    model = Category
    serializer_class = CategorySerializer
