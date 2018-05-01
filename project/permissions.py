from utils.permissions import IsAuthenticated


class IsAdmin(IsAuthenticated):
    async def has_permission(self, request):
        await super(IsAdmin, self).has_permission(request)
        user = request['user']
        return user.role == 3
