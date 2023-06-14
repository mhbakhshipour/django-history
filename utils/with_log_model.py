from typing import Tuple

from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from utils.model_log_record import LogRecord


def default_histories():
    return []


class WithLogModel(models.Model):
    histories = models.JSONField(
        default=default_histories, blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not is_new:
            self.histories = LogRecord(self).generate_log()

        super().save(*args, **kwargs)


PRE_CHANGE_FOR_PRE_REMOVE_ACTION = []


@receiver(m2m_changed)
def m2m_signal_handler(sender, **kwargs):
    instance = kwargs['instance']
    action = kwargs['action']
    pk_set = kwargs['pk_set']
    model_fields = list(map(lambda x: x.name, instance._meta.fields))

    if not "histories" in model_fields:
        return

    if action in ("pre_remove", "pre_add", "pre_clear"):
        m2m_fields = [field.name for field in instance._meta.many_to_many]
        old_histories = instance.histories or []

        for m2m_field in m2m_fields:
            if getattr(instance, m2m_field).source_field.model is sender:
                if action == "pre_remove":
                    pre_change, post_change = prepare_pre_remove_history(
                        instance, m2m_field, pk_set)
                elif action == "pre_add":
                    pre_change, post_change = prepare_pre_add_history(
                        instance, m2m_field, pk_set)
                elif action == "pre_clear":
                    pre_change, post_change = prepare_pre_clear_history(
                        instance, m2m_field, pk_set)
                else:
                    pre_change, post_change = [], []

                pr_data = {m2m_field: pre_change}
                next_data = {m2m_field: post_change}

                log_record = LogRecord(instance)
                request_user = log_record.prepare_request_user()

                new_history = log_record.prepare_result(
                    pr_data, next_data, old_histories, request_user)

        instance.__class__.objects.filter(
            pk=instance.id).update(histories=new_history)


def prepare_pre_remove_history(instance, m2m_field: str, pk_set: dict = {}) -> Tuple[list, list]:
    pre_change = [o.__str__() for o in getattr(instance, m2m_field).all()]
    post_change = [o.__str__() for o in getattr(
        instance, m2m_field).exclude(pk__in=pk_set)]
    global PRE_CHANGE_FOR_PRE_REMOVE_ACTION
    PRE_CHANGE_FOR_PRE_REMOVE_ACTION = pre_change

    return pre_change, post_change


def prepare_pre_add_history(instance, m2m_field: str, pk_set: dict = {}) -> Tuple[list, list]:
    pre_change = [o.__str__() for o in getattr(instance, m2m_field).all()]

    global PRE_CHANGE_FOR_PRE_REMOVE_ACTION
    if PRE_CHANGE_FOR_PRE_REMOVE_ACTION:
        pre_change = PRE_CHANGE_FOR_PRE_REMOVE_ACTION
        PRE_CHANGE_FOR_PRE_REMOVE_ACTION = []

    post_change = [o.__str__() for o in (getattr(instance, m2m_field).all(
    ) | getattr(instance, m2m_field).model.objects.filter(pk__in=pk_set))]
    post_change = list(set(post_change))

    return pre_change, post_change


def prepare_pre_clear_history(instance, m2m_field: str, pk_set: dict = {}) -> Tuple[list, list]:
    pre_change = [o.__str__() for o in getattr(instance, m2m_field).all()]
    post_change = []

    return pre_change, post_change
