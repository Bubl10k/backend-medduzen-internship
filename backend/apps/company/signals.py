import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from backend.apps.company.models import Company

logger = logging.getLogger("db_operations")


@receiver(post_save, sender=Company)
def log_company_save(sender, instance, created, **kwargs):
    if created:
        logger.info("Company created: %s (ID: %d)", instance.name, instance.id)
    else:
        logger.info("Company updated: %s (ID: %d)", instance.name, instance.id)


@receiver(post_delete, sender=Company)
def log_company_delete(sender, instance, **kwargs):
    logger.info("Company deleted: %s (ID: %d)", instance.name, instance.id)
