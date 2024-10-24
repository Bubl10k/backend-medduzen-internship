import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from backend.apps.users.models import CustomUser


logger = logging.getLogger('db_operations')

@receiver(post_save, sender=CustomUser)
def log_user_save(sender, instance, created, **kwargs):
    if created:
        logger.info('User created: %s (ID: %d)', instance.username, instance.id)
    else:
        logger.info('User updated: %s (ID: %d)', instance.username, instance.id)
        

@receiver(post_delete, sender=CustomUser)
def log_user_delete(sender, instance, **kwargs):
    logger.info('User deleted: %s (ID: %d)', instance.username, instance.id)
    