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


class ReviewView(APIView):
    permission_classes = [IsReviewer]

    def post(self, request):
        serializer = ReviewInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            review = submit_review(reviewer=request.user, **serializer.validated_data)
        except ReviewError as exc:
            return Response({"detail": str(exc)}, status=exc.status_code)
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class QueueView(APIView):
    permission_classes = [IsReviewer]

    def get(self, request):
        return Response(QueueSerializer(review_queue(request.user)[:20], many=True).data)


class StatsView(APIView):
    permission_classes = [IsReviewer]

    def get(self, request):
        return Response(StatsSerializer(reviewer_stats(request.user)).data)
