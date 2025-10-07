def has_permission(self, request, view, obj=None):
    return obj is None or obj.from_user == request.user
