__all__ = ('Contract', 'PaginationContract')

from rest_framework import serializers


class Contract(serializers.Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PaginationContract(Contract):
    previous = serializers.URLField(allow_null=True)
    next = serializers.URLField(allow_null=True)
    count = serializers.IntegerField()
