from datetime import datetime

from django.contrib.auth.models import User

from utils.model_to_dict import model_to_dict
from utils.current_request_middleware import current_request


class LogRecord:
    _instance = None

    def __init__(self, instance) -> None:
        self.instance = instance

    def __new__(cls, *args, **kwargs):
        """
        Singleton pattern implementation to ensure only one instance during runtime.
        """

        if not cls._instance:
            cls._instance = super(LogRecord, cls).__new__(cls)
        return cls._instance

    def generate_log(self) -> list:
        old_data = self.__prepare_old_data()
        old_histories = self.instance.histories or []

        if not old_data:
            return old_histories

        new_data = self.__prepare_new_data(old_data)

        request_user = self.prepare_request_user()

        result = self.prepare_result(
            old_data, new_data, old_histories, request_user)

        return result

    def __prepare_old_data(self) -> dict or None:
        changed_fields_with_old_value = self.__get_changed_fields_with_old_value()
        if not changed_fields_with_old_value:
            return None

        changed_fields_with_old_value_excluded_histories = self.__remove_history_field(
            changed_fields_with_old_value)

        if not changed_fields_with_old_value_excluded_histories:
            return None

        return changed_fields_with_old_value_excluded_histories

    def __get_changed_fields_with_old_value(self) -> dict:
        instance = self.instance

        changed_fields_with_old_value = {}
        old_instance = instance.__class__.objects.get(pk=instance.pk)
        for field in instance._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)

            if old_value != new_value:
                changed_fields_with_old_value[field.name] = (
                    old_value
                    if type(old_value) in [list, dict, int, bool, float, type(None)]
                    else old_value.__str__()
                )
        return changed_fields_with_old_value

    def __remove_history_field(self, changed_fields: dict) -> dict:
        # REMOVE HISTORY FEILDS FROM CHANGES
        if "histories" in changed_fields:
            changed_fields.pop("histories")

        return changed_fields

    def __prepare_new_data(self, old_data: dict) -> dict:
        instance = self.instance
        new_data = self.__get_new_data_from_model(instance, old_data)

        return new_data

    def __get_new_data_from_model(self, instance, old_data: dict) -> dict:
        new_data = model_to_dict(instance, fields=list(
            old_data.keys()), get_data_with_str=True)

        return new_data

    def prepare_request_user(self) -> User or None:
        user = current_request().user if current_request() else None

        return user

    def prepare_result(self, old_data: dict, new_data: dict, old_histories: list, request_user: User or None) -> list:
        old_histories.append(
            {
                "change_date": str(datetime.now()),
                "editor": self.__user_serializer(request_user),
                "previous_data": old_data,
                "next_data": new_data,
            }
        )
        return old_histories

    def __user_serializer(self, request_user: User or None) -> dict:
        if request_user:
            serialized_user = {
                "id": request_user.id,
                "username": request_user.username,
                "full_name": request_user.full_name,
                "avatar": request_user.avatar.url if request_user.avatar else None,
            }
        else:
            serialized_user = {
                "id": None,
                "username": "system",
                "full_name": "system",
                "avatar": None,
            }
        return serialized_user
