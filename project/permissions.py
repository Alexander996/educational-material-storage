from utils.permissions import IsAuthenticated

STUDENT = 1
TEACHER = 2
MODERATOR = 3
ADMIN = 4


class IsAdmin(IsAuthenticated):
    async def has_permission(self, request):
        await super(IsAdmin, self).has_permission(request)
        user = request['user']
        return user.role == ADMIN
