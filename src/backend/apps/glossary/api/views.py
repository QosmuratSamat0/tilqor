from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.glossary.api.serializers import (
    DailyCatalogueSerializer,
    DictionaryTermDetailSerializer,
    DictionaryTermSerializer,
    PaginatedDictionaryTermListSerializer,
)
from apps.glossary.errors import GlossaryError
from apps.glossary.selectors import daily_catalogue, dictionary_term_detail, dictionary_terms
from common.choices import Domain
from common.serializers import DetailErrorSerializer, FieldErrorsSerializer


class DictionaryPagination(PageNumberPagination):
    page_size = settings.TASK_LIST_PAGE_SIZE

    def get_page_size(self, request):
        return settings.TASK_LIST_PAGE_SIZE


class DictionaryListView(APIView):
    permission_classes = [AllowAny]
    pagination_class = DictionaryPagination

    @extend_schema(
        tags=["dictionary"],
        operation_id="dictionary_list",
        parameters=[
            OpenApiParameter(
                name="q",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Search by Russian term or eligible Kazakh variant.",
            ),
            OpenApiParameter(
                name="domain",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=Domain.values,
                required=False,
                description="Filter dictionary terms by domain.",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="1-based page number.",
            ),
        ],
        responses={
            200: PaginatedDictionaryTermListSerializer,
            400: FieldErrorsSerializer,
            404: DetailErrorSerializer,
        },
    )
    def get(self, request):
        q = request.query_params.get("q")
        domain = request.query_params.get("domain")
        try:
            terms = dictionary_terms(q=q, domain=domain)
        except GlossaryError as exc:
            return Response(exc.as_dict(), status=exc.status_code)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(terms, request, view=self)
        return paginator.get_paginated_response(
            DictionaryTermSerializer(page, many=True).data
        )


class DictionaryDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["dictionary"],
        operation_id="dictionary_retrieve",
        responses={
            200: DictionaryTermDetailSerializer,
            404: DetailErrorSerializer,
        },
    )
    def get(self, request, term_id: int):
        entry = dictionary_term_detail(
            term_id=term_id,
            include_pending=bool(request.user and request.user.is_authenticated),
        )
        if entry is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(DictionaryTermDetailSerializer(entry).data)


class DailyCatalogueView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["catalogue"],
        operation_id="catalogue_today_retrieve",
        parameters=[
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Optional ISO date (YYYY-MM-DD) in Asia/Almaty.",
            ),
        ],
        responses={
            200: DailyCatalogueSerializer,
            400: FieldErrorsSerializer,
        },
    )
    def get(self, request):
        raw_date = request.query_params.get("date")
        try:
            catalogue = daily_catalogue(raw_date=raw_date)
        except GlossaryError as exc:
            return Response(exc.as_dict(), status=exc.status_code)
        return Response(DailyCatalogueSerializer(catalogue).data)
