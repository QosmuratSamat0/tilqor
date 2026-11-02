from random import Random

from django.conf import settings
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contributions.api.serializers import (
    ContributionSubmissionSerializer,
    OwnContributionSerializer,
    PreferenceInputSerializer,
    PreferenceSerializer,
    TaskDetailSerializer,
    TaskSerializer,
    TextInputSerializer,
    VersionSubmissionSerializer,
)
from apps.contributions.errors import ContributionError
from apps.contributions.selectors import active_tasks, own_contributions, task_detail
from apps.contributions.services import set_preference, submit_contribution, submit_version


class TaskListPagination(PageNumberPagination):
    page_size = settings.TASK_LIST_PAGE_SIZE

    def get_page_size(self, request):
        return settings.TASK_LIST_PAGE_SIZE


class TaskListView(APIView):
    pagination_class = TaskListPagination

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
    def get(self, request, task_id: int):
        task = task_detail(task_id=task_id, user=request.user, rng=Random())
        if task is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(TaskDetailSerializer(task).data)


class TaskContributionView(APIView):
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
    def get(self, request):
        contributions = own_contributions(request.user)
        return Response(OwnContributionSerializer(contributions, many=True).data)


class ContributionVersionView(APIView):
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
