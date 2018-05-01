from apps.users.models import User

from apps.users.serializers import UserSerializer
from utils import views


class UsersView(views.ListView):
    model = User
    serializer_class = UserSerializer


class UserView(views.DetailView):
    model = User
    serializer_class = UserSerializer
    # queryset = User.c.username == 'admin'
