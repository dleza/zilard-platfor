from rest_framework import permissions, viewsets

from users.permissions import filter_workers_for_user, filter_workplaces_for_user, user_can_edit

from .models import DisabilityProfile, Worker, Workplace
from .serializers import DisabilityProfileSerializer, WorkerSerializer, WorkplaceSerializer


class EditRoleOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return user_can_edit(request.user)


class WorkerViewSet(viewsets.ModelViewSet):
    serializer_class = WorkerSerializer
    permission_classes = [EditRoleOrReadOnly]

    def get_queryset(self):
        queryset = Worker.objects.select_related("workplace", "disability_profile")
        return filter_workers_for_user(queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
            capture_source=Worker.CAPTURE_SOURCE_WEB,
            capture_mode=Worker.CAPTURE_MODE_ONLINE,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class DisabilityProfileViewSet(viewsets.ModelViewSet):
    serializer_class = DisabilityProfileSerializer
    permission_classes = [EditRoleOrReadOnly]

    def get_queryset(self):
        worker_ids = filter_workers_for_user(Worker.objects.all(), self.request.user).values("id")
        return DisabilityProfile.objects.filter(worker_id__in=worker_ids).select_related("worker")


class WorkplaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkplaceSerializer
    permission_classes = [EditRoleOrReadOnly]

    def get_queryset(self):
        return filter_workplaces_for_user(Workplace.objects.all(), self.request.user)
