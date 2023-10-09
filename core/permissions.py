from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
        Permissions to allow only the owner to modify the instance
        and allow others to only view it
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or obj.post_user == request.user:
            return True
        return False

class IsOwnerOrReadOnlyAccount(permissions.BasePermission):
    """
        Permissions to allow only the owner to modify the instance
        and allow others to only view it
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or obj.user == request.user:
            return True
        return False

class IsOwner(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsAdminAndStaffOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        staff = request.user.is_worker
        admin = request.user.is_admin
        if request.method in permissions.SAFE_METHODS or obj.user.admin == admin:
            return True

class IsEnroll(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.user in obj.enrolled.all():
            return super().has_object_permission(request, view, obj)
