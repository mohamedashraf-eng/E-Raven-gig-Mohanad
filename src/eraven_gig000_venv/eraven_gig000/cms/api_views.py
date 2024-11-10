from rest_framework import viewsets, permissions
from rest_framework.decorators import action  # Added import
from rest_framework.response import Response  # Ensure this is imported for Response
from django.contrib.auth import get_user_model
from .models import Course
from .serializers import CourseSerializer

from .models import (
    Assignment, Quiz, Challenge, Submission,
    UserProgress, PointTransaction, Ranking
)
from .serializers import (
    AssignmentSerializer, QuizSerializer, ChallengeSerializer,
    SubmissionSerializer, UserProgressSerializer,
    PointTransactionSerializer, RankingSerializer, UserSerializer
)
from .permissions import IsAuthorOrReadOnly

User = get_user_model()


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows assignments to be viewed or edited.
    """
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


class QuizViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows quizzes to be viewed or edited.
    """
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


class ChallengeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows challenges to be viewed or edited.
    """
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows submissions to be viewed or edited.
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Submission.objects.all()
        return Submission.objects.filter(user=self.request.user)


class UserProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user progress to be viewed or edited.
    """
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PointTransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows point transactions to be viewed or edited.
    """
    queryset = PointTransaction.objects.all()
    serializer_class = PointTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return PointTransaction.objects.all()
        return PointTransaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RankingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows rankings to be viewed.
    """
    queryset = Ranking.objects.all().order_by('-points')
    serializer_class = RankingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        user = self.get_object()
        submissions = user.submissions.all()
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        user = self.get_object()
        progresses = user.progresses.all()
        serializer = UserProgressSerializer(progresses, many=True)
        return Response(serializer.data)
    
class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows courses to be viewed.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Optionally, only return courses the user is enrolled in
        return user.enrolled_courses.all()
