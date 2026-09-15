from django.db.models import Count
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from feedback.models import StakeholderFeedback
from monitoring.models import ProjectActivity
from users.models import User
from users.permissions import filter_workers_for_user, filter_workplaces_for_user, user_can_edit
from workers.choices import (
    ACCESSIBILITY_STATUS_CHOICES,
    DISABILITY_TYPE_CHOICES,
    EMPLOYMENT_STATUS_CHOICES,
    GENDER_CHOICES,
    PROVINCE_CHOICES,
    PROVINCE_DISTRICTS,
    SECTOR_CHOICES,
    SEVERITY_CHOICES,
    UNION_MEMBERSHIP_CHOICES,
    WASHINGTON_GROUP_CHOICES,
)
from workers.models import LabourRightsRecord, Occupation, TradeUnion, Worker, Workplace

from .serializers import (
    MobileAuthTokenSerializer,
    MobileFeedbackSerializer,
    MobileLabourRightsRecordSerializer,
    MobileUserSerializer,
    MobileWorkerSerializer,
    MobileWorkplaceSerializer,
)


class EditRoleOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return user_can_edit(request.user)


def choice_payload(choices):
    return [{"value": value, "label": label} for value, label in choices]


class MobileLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = MobileAuthTokenSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user": MobileUserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class MobileMeView(APIView):
    def get(self, request):
        return Response(MobileUserSerializer(request.user).data)


class MobileLookupView(APIView):
    def get(self, request):
        workplaces = filter_workplaces_for_user(Workplace.objects.all(), request.user).order_by("employer_name")
        return Response(
            {
                "server_time": timezone.now(),
                "provinces": [
                    {
                        "value": province,
                        "label": label,
                        "districts": [{"value": district, "label": district} for district in PROVINCE_DISTRICTS[province]],
                    }
                    for province, label in PROVINCE_CHOICES
                ],
                "genders": choice_payload(GENDER_CHOICES),
                "sectors": choice_payload(SECTOR_CHOICES),
                "employment_statuses": choice_payload(EMPLOYMENT_STATUS_CHOICES),
                "union_membership_statuses": choice_payload(UNION_MEMBERSHIP_CHOICES),
                "disability_types": choice_payload(DISABILITY_TYPE_CHOICES),
                "severity_levels": choice_payload(SEVERITY_CHOICES),
                "washington_group_answers": choice_payload(WASHINGTON_GROUP_CHOICES),
                "accessibility_statuses": choice_payload(ACCESSIBILITY_STATUS_CHOICES),
                "labour_case_statuses": choice_payload(LabourRightsRecord.CASE_STATUS_CHOICES),
                "feedback_statuses": choice_payload(StakeholderFeedback.STATUS_CHOICES),
                "occupations": [
                    {
                        "id": occupation.id,
                        "name": occupation.name,
                        "sector": occupation.sector,
                    }
                    for occupation in Occupation.objects.filter(is_active=True).order_by("sort_order", "name")
                ],
                "trade_unions": [
                    {
                        "id": union.id,
                        "name": union.name,
                        "full_name": union.full_name,
                    }
                    for union in TradeUnion.objects.filter(is_active=True).order_by("sort_order", "name")
                ],
                "workplaces": [
                    {
                        "id": workplace.id,
                        "label": str(workplace),
                        "employer_name": workplace.employer_name,
                        "workplace_name": workplace.workplace_name,
                        "province": workplace.province,
                        "district": workplace.district,
                    }
                    for workplace in workplaces
                ],
            }
        )


class MobileDashboardSummaryView(APIView):
    def get(self, request):
        workers = filter_workers_for_user(Worker.objects.all(), request.user)
        workplaces = filter_workplaces_for_user(Workplace.objects.all(), request.user)
        disability_counts = (
            workers.values("disability_profile__disability_type")
            .annotate(total=Count("id"))
            .order_by("disability_profile__disability_type")
        )
        province_counts = [
            {"province": province, "total": workers.filter(province=province).count()}
            for province, _label in PROVINCE_CHOICES
        ]
        return Response(
            {
                "workers_total": workers.count(),
                "union_members": workers.filter(union_membership_status="member").count(),
                "verified_workers": workers.filter(data_verified=True).count(),
                "workplaces_total": workplaces.count(),
                "activities_total": ProjectActivity.objects.count(),
                "disability_breakdown": list(disability_counts),
                "province_distribution": province_counts,
            }
        )


class MobileWorkerViewSet(viewsets.ModelViewSet):
    serializer_class = MobileWorkerSerializer
    permission_classes = [EditRoleOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = Worker.objects.select_related("workplace", "disability_profile", "labour_rights")
        return filter_workers_for_user(queryset, self.request.user)

    def perform_create(self, serializer):
        capture_mode = self.request.data.get("capture_mode")
        if capture_mode not in {Worker.CAPTURE_MODE_ONLINE, Worker.CAPTURE_MODE_OFFLINE}:
            capture_mode = Worker.CAPTURE_MODE_ONLINE
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
            capture_source=Worker.CAPTURE_SOURCE_MOBILE,
            capture_mode=capture_mode,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class MobileWorkplaceViewSet(viewsets.ModelViewSet):
    serializer_class = MobileWorkplaceSerializer
    permission_classes = [EditRoleOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        return filter_workplaces_for_user(Workplace.objects.all(), self.request.user)


class MobileLabourRightsViewSet(viewsets.ModelViewSet):
    serializer_class = MobileLabourRightsRecordSerializer
    permission_classes = [EditRoleOrReadOnly]

    def get_queryset(self):
        worker_ids = filter_workers_for_user(Worker.objects.all(), self.request.user).values("id")
        return LabourRightsRecord.objects.filter(worker_id__in=worker_ids).select_related("worker").order_by("worker__last_name", "worker__first_name")

    def perform_create(self, serializer):
        worker = serializer.validated_data["worker"]
        allowed = filter_workers_for_user(Worker.objects.filter(pk=worker.pk), self.request.user).exists()
        if not allowed:
            raise PermissionDenied("You cannot create a labour-rights record for this worker.")
        serializer.save()


class MobileFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = MobileFeedbackSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_queryset(self):
        queryset = StakeholderFeedback.objects.select_related("user")
        user = self.request.user
        if user.is_superuser or user.role in {User.ROLE_SYSTEM_ADMIN, User.ROLE_NATIONAL_MANAGER}:
            return queryset
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        feedback = serializer.save(user=self.request.user)
        changed = False
        if not feedback.contact_name:
            feedback.contact_name = self.request.user.get_full_name() or self.request.user.username
            changed = True
        if not feedback.contact_email:
            feedback.contact_email = self.request.user.email
            changed = True
        if not feedback.role_or_group:
            feedback.role_or_group = self.request.user.get_role_display()
            changed = True
        if changed:
            feedback.save(update_fields=["contact_name", "contact_email", "role_or_group", "updated_at"])

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def mark_reviewed(self, request, pk=None):
        feedback = self.get_object()
        if not (request.user.is_superuser or request.user.role in {User.ROLE_SYSTEM_ADMIN, User.ROLE_NATIONAL_MANAGER}):
            raise PermissionDenied("Only project managers and admins can update feedback status.")
        feedback.status = StakeholderFeedback.STATUS_REVIEWED
        feedback.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(feedback).data)
