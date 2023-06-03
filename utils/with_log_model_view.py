from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


class WithLogModelViewSet(BaseModelViewSet):
    # EXCLUDE HISTORIES FIELD IN filter_fields !!
    filter_fields = []
    search_fields = "__all__"
    ordering_fields = "__all__"
    filter_backends = [SearchFilter, DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        has_pagination = request.GET.get("has_pagination", "true")

        if has_pagination == "false":
            self.pagination_class = None
        return super().list(request, *args, **kwargs)

    def get_serializer_context(self):
        return {"request": self.request}
