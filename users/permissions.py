from django.core.exceptions import PermissionDenied

from .models import User


ALL_DATA_ROLES = {
    User.ROLE_SYSTEM_ADMIN,
    User.ROLE_NATIONAL_MANAGER,
    User.ROLE_READ_ONLY,
}

WRITE_ROLES = {
    User.ROLE_SYSTEM_ADMIN,
    User.ROLE_NATIONAL_MANAGER,
    User.ROLE_UNION_FOCAL,
    User.ROLE_DATA_COLLECTOR,
}


def user_can_edit(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_superuser or user.role in WRITE_ROLES))


def require_edit_permission(user) -> None:
    if not user_can_edit(user):
        raise PermissionDenied("Your role does not allow editing records.")


def filter_workers_for_user(queryset, user):
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.is_superuser or user.role in ALL_DATA_ROLES:
        return queryset
    if user.assigned_union:
        return queryset.filter(union_name__iexact=user.assigned_union)
    # A union-scoped role (focal person / data collector) with no assigned_union
    # configured has no data they're entitled to see. Fail closed here, rather than
    # falling through to the unrestricted queryset, which would otherwise hand an
    # unconfigured account visibility into every union's records.
    return queryset.none()


def filter_workplaces_for_user(queryset, user):
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.is_superuser or user.role in ALL_DATA_ROLES:
        return queryset
    if user.assigned_union:
        return queryset.filter(workers__union_name__iexact=user.assigned_union).distinct()
    return queryset.none()
