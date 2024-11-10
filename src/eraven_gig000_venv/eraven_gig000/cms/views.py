# cms/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Article, Video, Post, Documentation, Course, Enrollment,
    Assignment, Quiz, Challenge, Submission,
    UserProgress, PointTransaction, Ranking
)
from .serializers import (
    ArticleSerializer, VideoSerializer, PostSerializer,
    DocumentationSerializer, CourseSerializer,
    AssignmentSerializer, QuizSerializer, ChallengeSerializer,
    SubmissionSerializer, UserProgressSerializer,
    PointTransactionSerializer, RankingSerializer, UserSerializer
)
from .forms import AssignmentSubmissionForm, QuizSubmissionForm
from .permissions import IsAuthorOrReadOnly
from ums.decorators import custom_login_required

User = get_user_model()

# =======================
# Standard Django Views
# =======================

def article_list(request):
    proficiency = request.GET.get('proficiency')
    articles = Article.objects.filter(proficiency_level=proficiency) if proficiency else Article.objects.all()
    return render(request, 'cms/article_list.html', {'articles': articles})


@custom_login_required
def article_detail(request, slug):
    # Retrieve the Article by slug
    article = get_object_or_404(Article, slug=slug)
    
    # Access the associated Course from the Article
    course = article.course
    
    # Check if the user is enrolled in the Course
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        return render(request, 'cms/access_denied.html', {'course': course})
    
    # Render the article detail template
    return render(request, 'cms/article_detail.html', {'article': article})


def video_list(request):
    proficiency = request.GET.get('proficiency')
    videos = Video.objects.filter(proficiency_level=proficiency) if proficiency else Video.objects.all()
    return render(request, 'cms/video_list.html', {'videos': videos})


def video_detail(request, slug):
    video = get_object_or_404(Video, slug=slug)
    return render(request, 'cms/video_detail.html', {'video': video})


def post_list(request):
    proficiency = request.GET.get('proficiency')
    posts = Post.objects.filter(proficiency_level=proficiency) if proficiency else Post.objects.all()
    return render(request, 'cms/post_list.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'cms/post_detail.html', {'post': post})


def documentation_list(request):
    proficiency = request.GET.get('proficiency')
    documents = Documentation.objects.filter(proficiency_level=proficiency) if proficiency else Documentation.objects.all()
    return render(request, 'cms/documentation_list.html', {'documents': documents})


def documentation_detail(request, slug):
    document = get_object_or_404(Documentation, slug=slug)
    return render(request, 'cms/documentation_detail.html', {'document': document})


def course_list(request):
    proficiency = request.GET.get('proficiency')
    courses = Course.objects.filter(proficiency_level=proficiency) if proficiency else Course.objects.all()
    return render(request, 'cms/course_list.html', {'courses': courses})


@custom_login_required
def course_detail_view(request, slug):
    course = get_object_or_404(Course, slug=slug)
    articles = Article.objects.filter(course=course)
    videos = Video.objects.filter(course=course)
    assignments = Assignment.objects.filter(course=course)
    quizzes = Quiz.objects.filter(course=course)
    challenges = Challenge.objects.filter(course=course)
    documentations = Documentation.objects.filter(course=course)

    context = {
        'course': course,
        'articles': articles,
        'videos': videos,
        'assignments': assignments,
        'quizzes': quizzes,
        'challenges': challenges,
        'documentations': documentations,
    }

    return render(request, 'cms/course_detail.html', context)

# =======================
# LMS Views
# =======================

@custom_login_required
def assignment_list(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    assignments = course.assignments.all()
    user_progress, _ = UserProgress.objects.get_or_create(user=request.user, course=course)
    
    context = {
        'course': course,
        'assignments': assignments,
        'user_progress': user_progress,
    }
    return render(request, 'cms/assignment_list.html', context)


@custom_login_required
def assignment_detail(request, course_slug, assignment_id):
    course = get_object_or_404(Course, slug=course_slug)
    assignment = get_object_or_404(Assignment, id=assignment_id, course=course)
    submissions = assignment.submissions.filter(user=request.user)
    
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.assignment = assignment
            submission.save()
            messages.success(request, 'Assignment submitted successfully!')
            update_user_progress(request.user, course)
            return redirect('cms:assignment_detail', course_slug=course.slug, assignment_id=assignment.id)
    else:
        form = AssignmentSubmissionForm()
    
    context = {
        'course': course,
        'assignment': assignment,
        'submissions': submissions,
        'form': form,
    }
    return render(request, 'cms/assignment_detail.html', context)


@custom_login_required
def quiz_list(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    quizzes = course.quizzes.all()
    user_progress, _ = UserProgress.objects.get_or_create(user=request.user, course=course)
    
    context = {
        'course': course,
        'quizzes': quizzes,
        'user_progress': user_progress,
    }
    return render(request, 'cms/quiz_list.html', context)


@custom_login_required
def quiz_detail(request, course_slug, quiz_id):
    # Ensure course and quiz are retrieved successfully
    course = get_object_or_404(Course, slug=course_slug)
    quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
    submissions = quiz.submissions.filter(user=request.user)
    
    if request.method == 'POST':
        form = QuizSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.quiz = quiz
            submission.save()
            # Grade submission with a safeguard
            if quiz and course:
                submission.grade = grade_submission(submission)
                submission.save()
                messages.success(request, 'Quiz submitted and graded successfully!')
                update_user_progress(request.user, course)
                return redirect('cms:quiz_detail', course_slug=course.slug, quiz_id=quiz.id)
            else:
                messages.error(request, 'Quiz or course data is missing.')
    else:
        form = QuizSubmissionForm()
    
    context = {
        'course': course,
        'quiz': quiz,
        'submissions': submissions,
        'form': form,
    }
    return render(request, 'cms/quiz_detail.html', context)

@custom_login_required
def challenge_list(request):
    today = timezone.now().date()
    challenges = Challenge.objects.filter()
    user_points = request.user.total_points
    
    return render(request, 'cms/challenge_list.html', {
        'challenges': challenges,
        'user_points': user_points,
    })

@custom_login_required
def challenge_detail_view(request, id):
    challenge = get_object_or_404(Challenge, id=id)
    course = challenge.course

    # Check if the user is enrolled in the course
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, "You must be enrolled in the course to view this challenge.")
        return redirect('cms:enrolled_courses')

    context = {
        'challenge': challenge,
        'course': course,
    }
    return render(request, 'cms/challenge_detail.html', context)

@custom_login_required
def participate_challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Optional: Check if the challenge is available today
    # if challenge.date != timezone.now().date():
    #     messages.error(request, 'This challenge is not available today.')
    #     return redirect('cms:challenge_list')
    
    # Check if the user has already participated in the challenge
    existing_submission = Submission.objects.filter(user=request.user, challenge=challenge).first()
    if existing_submission:
        messages.warning(request, 'You have already participated in this challenge.')
        return redirect('cms:challenge_list')
    
    # Create a submission for the challenge
    submission = Submission.objects.create(
        user=request.user,
        challenge=challenge,
        content="Participated in the challenge",
        grade=100 
    )

    messages.success(request, f'You participated in the challenge and earned {challenge.points} points!')
    return redirect('cms:challenge_list')

@custom_login_required
def user_progress_view(request):
    return render(request, 'cms/user_progress.html', {'progresses': request.user.progresses.all()})

@custom_login_required
def ranking_view(request):
    top_rankings = Ranking.objects.all().order_by('-points')[:10]
    return render(request, 'cms/ranking.html', {
        'rankings': top_rankings,
        'user_rank': request.user.ranking.rank,
    })

# =======================
# Helper Functions
# =======================

def update_user_progress(user, course):
    user_progress, created = UserProgress.objects.get_or_create(user=user, course=course)
    total_assignments = course.assignments.count()
    completed_assignments = course.assignments.filter(submissions__user=user, submissions__grade__gte=75).distinct().count()
    total_quizzes = course.quizzes.count()
    completed_quizzes = course.quizzes.filter(submissions__user=user, submissions__grade__gte=75).distinct().count()
    
    total_tasks = total_assignments + total_quizzes
    completed_tasks = completed_assignments + completed_quizzes
    
    progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    user_progress.progress_percentage = progress_percentage
    user_progress.completed = progress_percentage >= 100
    user_progress.save()


def grade_submission(submission):
    if submission.quiz:
        return 100  # Placeholder, replace with actual grading logic
    return None

# =======================
# Enrollment and Course Views
# =======================

@custom_login_required
def enroll_course_view(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    _, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    messages.success(request, f"Successfully enrolled in {course.title}." if created else f"You are already enrolled in {course.title}.")
    return redirect(reverse('cms:enrolled_courses'))


@custom_login_required
def available_courses_view(request):
    enrolled_courses = request.user.enrolled_courses.values_list('id', flat=True)
    available_courses = Course.objects.exclude(id__in=enrolled_courses)
    return render(request, 'cms/available_courses.html', {'available_courses': available_courses})

