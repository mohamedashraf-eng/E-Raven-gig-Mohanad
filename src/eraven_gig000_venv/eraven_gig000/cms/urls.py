# cms/urls.py

from django.urls import path, include
from rest_framework import routers
from . import views
from .api_views import (
    AssignmentViewSet, QuizViewSet, ChallengeViewSet,
    SubmissionViewSet, UserProgressViewSet, PointTransactionViewSet,
    RankingViewSet, UserViewSet, CourseViewSet
)

app_name = 'cms'

router = routers.DefaultRouter()
router.register(r'assignments', AssignmentViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'challenges', ChallengeViewSet)
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'user-progress', UserProgressViewSet, basename='userprogress')
router.register(r'point-transactions', PointTransactionViewSet, basename='pointtransaction')
router.register(r'rankings', RankingViewSet)
router.register(r'users', UserViewSet)
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    # API Routes
    path('api/', include((router.urls, 'api'), namespace='api')),

    # Standard Django Views
    path('courses/', views.course_list, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail_view, name='course_detail'),
    path('courses/<slug:course_slug>/assignments/', views.assignment_list, name='assignment_list'),
    path('courses/<slug:course_slug>/assignments/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('courses/<slug:course_slug>/quizzes/', views.quiz_list, name='quiz_list'),
    path('courses/<slug:course_slug>/quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),

    # Enrollment and available courses
    path('available-courses/', views.available_courses_view, name='available_courses'),
    path('enroll/<slug:course_slug>/', views.enroll_course_view, name='enroll_course'),

    # Article, video, post, and documentation views
    path('articles/', views.article_list, name='article_list'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('videos/', views.video_list, name='video_list'),
    path('videos/<slug:slug>/', views.video_detail, name='video_detail'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/<slug:slug>/', views.post_detail, name='post_detail'),
    path('documentations/', views.documentation_list, name='documentation_list'),
    path('documentations/<slug:slug>/', views.documentation_detail, name='documentation_detail'),

    # Challenge-related views
    path('challenges/', views.challenge_list, name='challenge_list'),
    path('challenges/<int:id>/', views.challenge_detail_view, name='challenge_detail'),
    path('challenges/<int:challenge_id>/participate/', views.participate_challenge, name='participate_challenge'),

    # User progress and rankings
    path('user/progress/', views.user_progress_view, name='user_progress'),
    path('rankings/', views.ranking_view, name='ranking'),
]
