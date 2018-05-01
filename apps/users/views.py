from apps.users.models import User

from apps.users.serializers import UserSerializer
from utils import views


class UsersView(views.ListView):
    model = User
    serializer_class = UserSerializer

    def get_queryset(self):
        blocked = self.request.query.get('blocked')
        if blocked is not None and blocked.lower() == 'true':
            return User.c.blocked == True
        else:
            return User.c.blocked == False


class UserView(views.DetailView):
    model = User
    serializer_class = UserSerializer
