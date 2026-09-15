from django.contrib.auth import authenticate
from rest_framework import serializers

from feedback.models import StakeholderFeedback
from users.models import User
from workers.choices import PROVINCE_DISTRICTS
from workers.models import DisabilityProfile, LabourRightsRecord, Worker, Workplace


class MobileUserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "role_display",
            "organisation",
            "assigned_union",
            "is_staff",
            "is_superuser",
        ]


class MobileAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)

    def validate(self, attrs):
        request = self.context.get("request")
        user = authenticate(request=request, username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Unable to log in with the provided credentials.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        attrs["user"] = user
        return attrs


class MobileWorkplaceSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="__str__", read_only=True)

    def validate(self, attrs):
        province = attrs.get("province", getattr(self.instance, "province", None))
        district = attrs.get("district", getattr(self.instance, "district", None))
        if province and district and district not in PROVINCE_DISTRICTS.get(province, []):
            raise serializers.ValidationError({"district": "Select a district that belongs to the selected province."})
        return attrs

    class Meta:
        model = Workplace
        fields = [
            "id",
            "label",
            "employer_name",
            "workplace_name",
            "province",
            "district",
            "address",
            "sector",
            "latitude",
            "longitude",
            "accessibility_status",
            "accommodations_available",
            "union_presence",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class NestedDisabilityProfileSerializer(serializers.ModelSerializer):
    disability_type_display = serializers.CharField(source="get_disability_type_display", read_only=True)
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)

    class Meta:
        model = DisabilityProfile
        fields = [
            "id",
            "disability_type",
            "disability_type_display",
            "other_disability_type",
            "severity",
            "severity_display",
            "assistive_devices",
            "accommodation_requirements",
            "accessibility_challenges",
            "functional_limitations",
            "wg_seeing",
            "wg_hearing",
            "wg_walking",
            "wg_remembering",
            "wg_self_care",
            "wg_communicating",
        ]
        read_only_fields = ["id", "disability_type_display", "severity_display"]


class NestedLabourRightsRecordSerializer(serializers.ModelSerializer):
    case_status_display = serializers.CharField(source="get_case_status_display", read_only=True)

    class Meta:
        model = LabourRightsRecord
        fields = [
            "id",
            "grievance_reported",
            "grievance_summary",
            "case_status",
            "case_status_display",
            "legal_support_provided",
            "collective_bargaining_coverage",
            "social_protection_coverage",
        ]
        read_only_fields = ["id", "case_status_display"]


class MobileWorkerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    workplace_label = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    captured_by = serializers.CharField(source="captured_by_display", read_only=True)
    capture_source_display = serializers.CharField(source="get_capture_source_display", read_only=True)
    capture_mode_display = serializers.CharField(source="get_capture_mode_display", read_only=True)
    disability_profile = NestedDisabilityProfileSerializer(required=False, allow_null=True)
    labour_rights = NestedLabourRightsRecordSerializer(required=False, allow_null=True)

    def get_workplace_label(self, obj):
        return str(obj.workplace) if obj.workplace else ""

    def get_photo_url(self, obj):
        request = self.context.get("request")
        if not obj.photo:
            return ""
        url = obj.photo.url
        return request.build_absolute_uri(url) if request else url

    def validate(self, attrs):
        province = attrs.get("province", getattr(self.instance, "province", None))
        district = attrs.get("district", getattr(self.instance, "district", None))
        if province and district and district not in PROVINCE_DISTRICTS.get(province, []):
            raise serializers.ValidationError({"district": "Select a district that belongs to the selected province."})
        return attrs

    def create(self, validated_data):
        disability_data = validated_data.pop("disability_profile", None)
        labour_data = validated_data.pop("labour_rights", None)
        worker = Worker.objects.create(**validated_data)
        if disability_data:
            DisabilityProfile.objects.create(worker=worker, **disability_data)
        if labour_data:
            LabourRightsRecord.objects.create(worker=worker, **labour_data)
        return worker

    def update(self, instance, validated_data):
        disability_data = validated_data.pop("disability_profile", None)
        labour_data = validated_data.pop("labour_rights", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        if disability_data is not None:
            profile, _created = DisabilityProfile.objects.get_or_create(
                worker=instance,
                defaults={
                    "disability_type": disability_data.get("disability_type", "other"),
                    "severity": disability_data.get("severity", "mild"),
                },
            )
            for field, value in disability_data.items():
                setattr(profile, field, value)
            profile.save()

        if labour_data is not None:
            labour, _created = LabourRightsRecord.objects.get_or_create(worker=instance)
            for field, value in labour_data.items():
                setattr(labour, field, value)
            labour.save()

        return instance

    class Meta:
        model = Worker
        fields = [
            "id",
            "unique_id",
            "full_name",
            "first_name",
            "last_name",
            "other_names",
            "national_id",
            "nationality",
            "gender",
            "date_of_birth",
            "age",
            "phone",
            "email",
            "province",
            "district",
            "workplace",
            "workplace_label",
            "sector",
            "occupation",
            "employment_status",
            "union_membership_status",
            "union_name",
            "leadership_participation",
            "committee_participation",
            "organising_activities",
            "latitude",
            "longitude",
            "photo",
            "photo_url",
            "consent_to_store_data",
            "data_verified",
            "capture_source",
            "capture_source_display",
            "capture_mode",
            "capture_mode_display",
            "captured_at_device",
            "captured_by",
            "disability_profile",
            "labour_rights",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "unique_id",
            "full_name",
            "age",
            "photo_url",
            "capture_source",
            "capture_source_display",
            "capture_mode_display",
            "captured_by",
            "created_at",
            "updated_at",
        ]


class MobileLabourRightsRecordSerializer(NestedLabourRightsRecordSerializer):
    worker_label = serializers.CharField(source="worker.full_name", read_only=True)

    class Meta(NestedLabourRightsRecordSerializer.Meta):
        model = LabourRightsRecord
        fields = ["worker", "worker_label"] + NestedLabourRightsRecordSerializer.Meta.fields


class MobileFeedbackSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    submitted_by = serializers.CharField(source="user.get_username", read_only=True)

    class Meta:
        model = StakeholderFeedback
        fields = [
            "id",
            "contact_name",
            "contact_email",
            "role_or_group",
            "page_url",
            "comment",
            "status",
            "status_display",
            "submitted_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "status_display", "submitted_by", "created_at", "updated_at"]
