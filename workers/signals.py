from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from core.middleware import get_current_user
from core.models import AuditLog

from .models import AccessibilityAudit, DisabilityProfile, LabourRightsRecord, Worker, WorkerDocument, Workplace


def _actor():
    user = get_current_user()
    if getattr(user, "is_authenticated", False):
        return user
    return None


def _log(instance, action: str, created: bool | None = None):
    if created is True:
        action = AuditLog.ACTION_CREATE
    elif created is False and action == AuditLog.ACTION_UPDATE:
        action = AuditLog.ACTION_UPDATE
    AuditLog.objects.create(
        actor=_actor(),
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(getattr(instance, "pk", "")),
        object_label=str(instance)[:255],
    )


@receiver(post_save, sender=Worker)
@receiver(post_save, sender=Workplace)
@receiver(post_save, sender=DisabilityProfile)
@receiver(post_save, sender=LabourRightsRecord)
@receiver(post_save, sender=WorkerDocument)
@receiver(post_save, sender=AccessibilityAudit)
def audit_saved(sender, instance, created, **kwargs):
    _log(instance, AuditLog.ACTION_UPDATE, created=created)


@receiver(post_delete, sender=Worker)
@receiver(post_delete, sender=Workplace)
@receiver(post_delete, sender=DisabilityProfile)
@receiver(post_delete, sender=LabourRightsRecord)
@receiver(post_delete, sender=WorkerDocument)
@receiver(post_delete, sender=AccessibilityAudit)
def audit_deleted(sender, instance, **kwargs):
    _log(instance, AuditLog.ACTION_DELETE)
