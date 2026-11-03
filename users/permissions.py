from django.core.exceptions import PermissionDenied
from django.db.models import Q

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
    # Union-scoped roles (focal person / data collector) always see the records they captured
    # themselves, plus every record of their assigned union. Without this, a collector could not
    # see a worker they had just entered if the worker's union differed from their assigned union,
    # or if they had no assigned union.
    own_records = Q(created_by=user)
    if user.assigned_union:
        return queryset.filter(Q(union_name__iexact=user.assigned_union) | own_records)
    return queryset.filter(own_records)


def filter_workplaces_for_user(queryset, user):
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.is_superuser or user.role in ALL_DATA_ROLES:
        return queryset
    # Union-scoped roles also see the workplaces they added themselves.
    own_workplaces = Q(created_by=user)
    if user.assigned_union:
        return queryset.filter(Q(workers__union_name__iexact=user.assigned_union) | own_workplaces).distinct()
    return queryset.filter(own_workplaces)
