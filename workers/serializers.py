from rest_framework import serializers

from .models import DisabilityProfile, LabourRightsRecord, Worker, Workplace
from .choices import PROVINCE_DISTRICTS


class WorkplaceSerializer(serializers.ModelSerializer):
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
            "created_at",
            "updated_at",
        ]


class DisabilityProfileSerializer(serializers.ModelSerializer):
    disability_type_display = serializers.CharField(source="get_disability_type_display", read_only=True)

    class Meta:
        model = DisabilityProfile
        fields = [
            "id",
            "worker",
            "disability_type",
            "disability_type_display",
            "other_disability_type",
            "severity",
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


class LabourRightsRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabourRightsRecord
        fields = [
            "grievance_reported",
            "case_status",
            "legal_support_provided",
            "collective_bargaining_coverage",
            "social_protection_coverage",
        ]


class WorkerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    disability_profile = DisabilityProfileSerializer(read_only=True)
    workplace_label = serializers.SerializerMethodField()
    captured_by = serializers.CharField(source="captured_by_display", read_only=True)
    capture_source_display = serializers.CharField(source="get_capture_source_display", read_only=True)
    capture_mode_display = serializers.CharField(source="get_capture_mode_display", read_only=True)

    def get_workplace_label(self, obj):
        return str(obj.workplace) if obj.workplace else ""

    def validate(self, attrs):
        province = attrs.get("province", getattr(self.instance, "province", None))
        district = attrs.get("district", getattr(self.instance, "district", None))
        if province and district and district not in PROVINCE_DISTRICTS.get(province, []):
            raise serializers.ValidationError({"district": "Select a district that belongs to the selected province."})
        return attrs

    class Meta:
        model = Worker
        fields = [
            "id",
            "unique_id",
            "full_name",
            "first_name",
            "last_name",
            "other_names",
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
            "latitude",
            "longitude",
            "data_verified",
            "capture_source",
            "capture_source_display",
            "capture_mode",
            "capture_mode_display",
            "captured_at_device",
            "captured_by",
            "disability_profile",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "unique_id",
            "capture_source",
            "capture_source_display",
            "capture_mode_display",
            "captured_by",
            "created_at",
            "updated_at",
        ]
