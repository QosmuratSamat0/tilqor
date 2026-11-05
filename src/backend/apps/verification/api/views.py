from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.verification.api.serializers import (
    QueueSerializer,
    ReviewInputSerializer,
    ReviewSerializer,
    StatsSerializer,
)
from apps.verification.selectors import review_queue, reviewer_stats
from apps.verification.services import submit_review
from apps.verification.services.errors import ReviewError
from common.permissions import IsReviewer
from common.serializers import AnyErrorSerializer, DetailErrorSerializer


class ReviewView(APIView):
    permission_classes = [IsReviewer]

    @extend_schema(
        tags=["reviews"],
        request=ReviewInputSerializer,
        responses={
            201: ReviewSerializer,
            400: AnyErrorSerializer,
            403: DetailErrorSerializer,
            409: DetailErrorSerializer,
        },
    )
    def post(self, request):
        serializer = ReviewInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            review = submit_review(reviewer=request.user, **serializer.validated_data)
        except ReviewError as exc:
            return Response(exc.as_dict(), status=exc.status_code)
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class QueueView(APIView):
    permission_classes = [IsReviewer]

    @extend_schema(
        tags=["reviews"],
        responses={200: QueueSerializer(many=True), 403: DetailErrorSerializer},
    )
    def get(self, request):
        return Response(QueueSerializer(review_queue(request.user)[:20], many=True).data)


class StatsView(APIView):
    permission_classes = [IsReviewer]

    @extend_schema(
        tags=["reviews"],
        responses={200: StatsSerializer, 403: DetailErrorSerializer},
    )
    def get(self, request):
        return Response(StatsSerializer(reviewer_stats(request.user)).data)
