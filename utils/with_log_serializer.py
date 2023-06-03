from rest_framework import serializers


class WithLogserializer(serializers.ModelSerializer):
    histories = serializers.ReadOnlyField()
