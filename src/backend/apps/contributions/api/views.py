from random import Random

from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contributions.api.serializers import (
    ContributionSubmissionSerializer,
    OwnContributionSerializer,
    PaginatedTaskListSerializer,
    PreferenceInputSerializer,
    PreferenceSerializer,
    TaskDetailSerializer,
    TaskSerializer,
    TextInputSerializer,
    VersionSubmissionSerializer,
)
from apps.contributions.errors import ContributionError
from apps.contributions.models import Task
from apps.contributions.selectors import active_tasks, own_contributions, task_detail
from apps.contributions.services import set_preference, submit_contribution, submit_version
from common.choices import Domain
from common.serializers import ErrorSerializer


class TaskListPagination(PageNumberPagination):
    page_size = settings.TASK_LIST_PAGE_SIZE

    def get_page_size(self, request):
        return settings.TASK_LIST_PAGE_SIZE


class TaskListView(APIView):
    pagination_class = TaskListPagination

    @extend_schema(
        tags=["tasks"],
        operation_id="tasks_list",
        parameters=[
            OpenApiParameter(
                name="domain",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=Domain.values,
                required=False,
                description="Filter active tasks by domain.",
            ),
            OpenApiParameter(
                name="type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=Task.Type.values,
                required=False,
                description="Filter active tasks by task type.",
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
            200: PaginatedTaskListSerializer,
            400: ErrorSerializer,
            403: ErrorSerializer,
            404: ErrorSerializer,
        },
    )
    def get(self, request):
        domain = request.query_params.get("domain")
        task_type = request.query_params.get("type")
        try:
            tasks = active_tasks(domain=domain, task_type=task_type)
        except ContributionError as exc:
            return Response(exc.as_dict(), status=exc.status_code)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tasks, request, view=self)
        return paginator.get_paginated_response(TaskSerializer(page, many=True).data)


class TaskDetailView(APIView):
    @extend_schema(
        tags=["tasks"],
        operation_id="tasks_retrieve",
        responses={
            200: TaskDetailSerializer,
            403: ErrorSerializer,
            404: ErrorSerializer,
        },
    )
    def get(self, request, task_id: int):
        task = task_detail(task_id=task_id, user=request.user, rng=Random())
        if task is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(TaskDetailSerializer(task).data)


class TaskContributionView(APIView):
    @extend_schema(
        tags=["tasks"],
        request=TextInputSerializer,
        responses={
            201: ContributionSubmissionSerializer,
            400: ErrorSerializer,
            403: ErrorSerializer,
            409: ErrorSerializer,
        },
    )
    def post(self, request, task_id: int):
        serializer = TextInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = submit_contribution(
                author=request.user,
                task_id=task_id,
                text_kk=serializer.validated_data["text_kk"],
            )
        except ContributionError as exc:
            return Response(exc.as_dict(), status=exc.status_code)
        return Response(
            ContributionSubmissionSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )


class TaskPreferenceView(APIView):
    @extend_schema(
        tags=["tasks"],
        request=PreferenceInputSerializer,
        responses={
            200: PreferenceSerializer,
            400: ErrorSerializer,
            403: ErrorSerializer,
            409: ErrorSerializer,
        },
    )
    def put(self, request, task_id: int):
        serializer = PreferenceInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            preference = set_preference(
                user=request.user,
                task_id=task_id,
                version_id=serializer.validated_data["version_id"],
            )
        except ContributionError as exc:
            return Response(exc.as_dict(), status=exc.status_code)
        return Response(PreferenceSerializer(preference).data)


class MyContributionsView(APIView):
    @extend_schema(
        tags=["contributions"],
        responses={
            200: OwnContributionSerializer(many=True),
            403: ErrorSerializer,
        },
    )
    def get(self, request):
        contributions = own_contributions(request.user)
        return Response(OwnContributionSerializer(contributions, many=True).data)


class ContributionVersionView(APIView):
    @extend_schema(
        tags=["contributions"],
        request=TextInputSerializer,
        responses={
            201: VersionSubmissionSerializer,
            400: ErrorSerializer,
            403: ErrorSerializer,
            409: ErrorSerializer,
        },
    )
    def post(self, request, contribution_id: int):
        serializer = TextInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = submit_version(
                author=request.user,
                contribution_id=contribution_id,
                text_kk=serializer.validated_data["text_kk"],
            )
        except ContributionError as exc:
            return Response(exc.as_dict(), status=exc.status_code)
        return Response(
            VersionSubmissionSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )
