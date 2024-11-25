# cms/views.py

from django.shortcuts import render, get_object_or_404, redirect
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
    UserProgress, PointTransaction, Ranking, Workshop, ArticleRead, DocumentationRead, Session
)
from .serializers import (
    ArticleSerializer, VideoSerializer, PostSerializer,
    DocumentationSerializer, CourseSerializer,
    AssignmentSerializer, QuizSerializer, ChallengeSerializer,
    SubmissionSerializer, UserProgressSerializer,
    PointTransactionSerializer, RankingSerializer, UserSerializer
)
from .forms import DocumentationReadForm, ArticleReadForm, QuizSubmissionForm, AssignmentSubmissionForm
from .permissions import IsAuthorOrReadOnly
from ums.decorators import custom_login_required
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from itertools import chain
from operator import attrgetter

User = get_user_model()

# =======================
# Standard Django Views
# =======================

def article_list(request):
    proficiency = request.GET.get('proficiency')
    articles = Article.objects.filter(proficiency_level=proficiency) if proficiency else Article.objects.all()
    if not articles.exists():
        messages.info(request, "No articles found for the selected proficiency level.")
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
        messages.error(request, f"You must be enrolled in {course.title} to view this article.")
        return render(request, 'cms/access_denied.html', {'course': course})
    
    # Render the article detail template
    return render(request, 'cms/article_detail.html', {'article': article})


def video_list(request):
    proficiency = request.GET.get('proficiency')
    videos = Video.objects.filter(proficiency_level=proficiency) if proficiency else Video.objects.all()
    if not videos.exists():
        messages.info(request, "No videos found for the selected proficiency level.")
    return render(request, 'cms/video_list.html', {'videos': videos})


def video_detail(request, slug):
    video = get_object_or_404(Video, slug=slug)
    return render(request, 'cms/video_detail.html', {'video': video})


def post_list(request):
    proficiency = request.GET.get('proficiency')
    posts = Post.objects.filter(proficiency_level=proficiency) if proficiency else Post.objects.all()
    if not posts.exists():
        messages.info(request, "No posts found for the selected proficiency level.")
    return render(request, 'cms/post_list.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'cms/post_detail.html', {'post': post})


def documentation_list(request):
    proficiency = request.GET.get('proficiency')
    documents = Documentation.objects.filter(proficiency_level=proficiency) if proficiency else Documentation.objects.all()
    if not documents.exists():
        messages.info(request, "No documentation found for the selected proficiency level.")
    return render(request, 'cms/documentation_list.html', {'documents': documents})


def documentation_detail(request, slug):
    document = get_object_or_404(Documentation, slug=slug)
    return render(request, 'cms/documentation_detail.html', {'document': document})


def course_list(request):
    proficiency = request.GET.get('proficiency')
    courses = Course.objects.filter(proficiency_level=proficiency) if proficiency else Course.objects.all()
    if not courses.exists():
        messages.info(request, "No courses available for the selected proficiency level.")
    return render(request, 'cms/course_list.html', {'courses': courses})

def course_detail_view(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    # Fetch all timeline-related items
    assignments = Assignment.objects.filter(course=course)
    challenges = Challenge.objects.filter(course=course)
    articles = Article.objects.filter(course=course)
    videos = Video.objects.filter(course=course)
    sessions = Session.objects.filter(course=course)
    documentations = Documentation.objects.filter(course=course)
    
    # Combine all items into a single list
    combined_timeline = list(chain(
        assignments, 
        challenges, 
        articles, 
        videos, 
        sessions, 
        documentations
    ))
    
    # Define a key function to extract the relevant date
    def get_date(item):
        if hasattr(item, 'due_date'):
            return item.due_date
        elif hasattr(item, 'date'):
            return item.date
        elif hasattr(item, 'created_at'):
            return item.created_at
        elif hasattr(item, 'date_time'):
            return item.date_time
        return None
    
    # Sort the combined timeline by date in descending order
    combined_timeline.sort(key=lambda x: get_date(x) or '', reverse=True)
    
    icon_map = {
        "Assignment": "fas fa-file-alt",
        "Challenge": "fas fa-trophy",
        "Article": "fas fa-newspaper",
        "Video": "fas fa-video",
        "Session": "fas fa-calendar-alt",
        "Documentation": "fas fa-book",
    }
        
    for item in combined_timeline:
        item.icon = icon_map.get(item.__class__.__name__, "fas fa-info-circle")
        
    context = {
        'course': course,
        'assignments': assignments,
        'challenges': challenges,
        'articles': articles,
        'videos': videos,
        'sessions': sessions,
        'documentations': documentations,
        # 'related_courses': get_related_courses(course),
        'combined_timeline': combined_timeline,  # Add the combined timeline to context
    }
    
    return render(request, 'cms/course_detail.html', context)

# =======================
# LMS Views
# =======================

def session_detail(request, course_slug):
    # Implementation pending
    messages.info(request, "Session details are coming soon.")
    return redirect('cms:course_detail', slug=course_slug)

def workshop_detail(request, course_slug):
    # Implementation pending
    messages.info(request, "Workshop details are coming soon.")
    return redirect('cms:course_detail', slug=course_slug)

@custom_login_required
def assignment_list(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    assignments = course.assignments.all()
    user_progress, _ = UserProgress.objects.get_or_create(user=request.user, course=course)
    
    if not assignments.exists():
        messages.info(request, f"No assignments available for {course.title} at this time.")
    
    context = {
        'course': course,
        'assignments': assignments,
        'user_progress': user_progress,
    }
    return render(request, 'cms/assignment_list.html', context)

@custom_login_required
def assignment_detail(request, course_slug, assignment_id):
    # Retrieve course and assignment objects
    course = get_object_or_404(Course, slug=course_slug)
    assignment = get_object_or_404(Assignment, id=assignment_id, course=course)
    
    # Define content_type for assignment submissions if using GenericForeignKey
    assignment_content_type = ContentType.objects.get_for_model(Assignment)
    
    # Adjust submission filter based on whether 'assignment' is a direct foreign key or GenericForeignKey
    submissions = Submission.objects.filter(
        user=request.user,
        content_type=assignment_content_type,
        object_id=assignment.id
    )
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to submit assignments.")
            return redirect('api:sign-in')
        
        # Check if submission already exists
        if submissions.exists():
            messages.warning(request, "You have already submitted this assignment.")
            return redirect('cms:assignment_detail', course_slug=course.slug, assignment_id=assignment.id)
        
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the submission with form data
            submission = form.save(commit=False)
            submission.user = request.user
            submission.content_type = assignment_content_type
            submission.object_id = assignment.id
            submission.save()
            
            messages.success(request, "Assignment submitted successfully!")
            update_user_progress(request.user, course)
            return redirect('cms:assignment_detail', course_slug=course.slug, assignment_id=assignment.id)
        else:
            messages.error(request, "Please correct the errors below in your assignment submission.")
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
    
    if not quizzes.exists():
        messages.info(request, f"No quizzes available for {course.title} at this time.")
    
    context = {
        'course': course,
        'quizzes': quizzes,
        'user_progress': user_progress,
    }
    return render(request, 'cms/quiz_list.html', context)


@custom_login_required
def quiz_detail(request, course_slug, quiz_id):
    course = get_object_or_404(Course, slug=course_slug)
    quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
    submissions = quiz.submissions.filter(user=request.user)
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to submit quizzes.")
            return redirect('api:sign-in')
        
        if submissions.exists():
            messages.warning(request, "You have already submitted this quiz.")
            return redirect('cms:quiz_detail', course_slug=course.slug, quiz_id=quiz.id)
        
        form = QuizSubmissionForm(request.POST)
        if form.is_valid():
            # Create the submission without any form fields
            Submission.objects.create(
                user=request.user,
                quiz=quiz,
                content="",  # Empty content as no form fields are filled
                # 'grade' can remain null until graded
                # 'points_awarded' can be handled separately based on grading
            )
            messages.success(request, "Quiz submitted successfully!")
            update_user_progress(request.user, course)
            return redirect('cms:quiz_detail', course_slug=course.slug, quiz_id=quiz.id)
        else:
            messages.error(request, "Please correct the errors below in your quiz submission.")
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
    
    if not challenges.exists():
        messages.info(request, "No challenges available at this time.")
    
    return render(request, 'cms/challenge_list.html', {
        'challenges': challenges,
        'user_points': user_points,
    })

@custom_login_required
def participate_challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Optional: Check if the challenge is available today
    # if challenge.date != timezone.now().date():
    #     messages.error(request, 'This challenge is not available today.')
    #     return redirect('cms:challenge_list')
    
    # Get the ContentType for Challenge
    challenge_content_type = ContentType.objects.get_for_model(Challenge)
    
    # Check if the user has already participated in the challenge
    existing_submission = Submission.objects.filter(
        user=request.user,
        content_type=challenge_content_type,
        object_id=challenge.id
    ).exists()
    
    if existing_submission:
        messages.warning(request, 'You have already participated in this challenge.')
        return redirect('cms:challenge_list')
    
    # Create a submission for the challenge
    Submission.objects.create(
        user=request.user,
        content_type=challenge_content_type,
        object_id=challenge.id,
        grade=100  # Assuming full marks for participation
    )
    
    messages.success(request, f'You participated in the challenge and earned {challenge.points} points!')
    return redirect('cms:challenge_detail', challenge_id=challenge.id)

@custom_login_required
def challenge_detail_view(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Get the ContentType for Challenge
    challenge_content_type = ContentType.objects.get_for_model(Challenge)
    
    # Determine if the user has already participated
    registered = Submission.objects.filter(
        user=request.user,
        content_type=challenge_content_type,
        object_id=challenge.id
    ).exists()
    
    context = {
        'challenge': challenge,
        'registered': registered,
    }
    
    if registered:
        messages.info(request, "You have already participated in this challenge.")
    
    return render(request, 'cms/challenge_detail.html', context)

@custom_login_required
def user_progress_view(request):
    progresses = request.user.progresses.all()
    if not progresses.exists():
        messages.info(request, "You have not made any progress yet.")
    return render(request, 'cms/user_progress.html', {'progresses': progresses})

@custom_login_required
def ranking_view(request):
    top_rankings = Ranking.objects.all().order_by('-points')[:10]
    try:
        user_rank = request.user.ranking.rank
    except Ranking.DoesNotExist:
        user_rank = None
        messages.info(request, "You are not ranked yet.")
    
    context = {
        'rankings': top_rankings,
        'user_rank': user_rank,
    }
    
    if user_rank:
        messages.success(request, f"Your current rank is #{user_rank}. Keep up the good work!")
    
    return render(request, 'cms/ranking.html', context)

# =======================
# Helper Functions
# =======================

def update_user_progress(user, course):
    user_progress, created = UserProgress.objects.get_or_create(user=user, course=course)

    # Calculate completed assignments by filtering Submission objects related to assignments
    completed_assignments = Submission.objects.filter(
        content_type__model='assignment',
        object_id__in=course.assignments.values_list('id', flat=True),
        user=user,
        grade__gte=75
    ).distinct().count()
    
    # Calculate completed quizzes by filtering Submission objects related to quizzes
    completed_quizzes = Submission.objects.filter(
        content_type__model='quiz',
        object_id__in=course.quizzes.values_list('id', flat=True),
        user=user,
        grade__gte=75
    ).distinct().count()
    
    # Calculate totals
    total_assignments = course.assignments.count()
    total_quizzes = course.quizzes.count()
    
    total_tasks = total_assignments + total_quizzes
    completed_tasks = completed_assignments + completed_quizzes
    
    # Calculate progress percentage
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
    # Create enrollment record
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    
    # Create or get UserProgress for the user and course
    UserProgress.objects.get_or_create(user=request.user, course=course)
    
    # Feedback message for enrollment
    if created:
        messages.success(request, f"Successfully enrolled in {course.title}.")
    else:
        messages.info(request, f"You are already enrolled in {course.title}.")
    
    return redirect(reverse('enrolled_courses'))

@custom_login_required
def available_courses_view(request):
    enrolled_courses = request.user.enrolled_courses.values_list('id', flat=True)
    available_courses = Course.objects.exclude(id__in=enrolled_courses)
    
    if not available_courses.exists():
        messages.info(request, "No available courses to enroll at this time.")
    
    return render(request, 'cms/available_courses.html', {'available_courses': available_courses})

@custom_login_required
def attend_workshop(request, workshop_id):
    """
    View to handle attending a workshop by spending points.
    """
    workshop = get_object_or_404(Workshop, id=workshop_id)
    user = request.user

    # Get the ContentType for Workshop
    workshop_content_type = ContentType.objects.get_for_model(Workshop)

    # Check if the user has already attended the workshop
    already_attended = Submission.objects.filter(
        user=user,
        content_type=workshop_content_type,
        object_id=workshop.id
    ).exists()

    if already_attended:
        messages.info(request, "You have already attended this workshop.")
        return redirect('cms:course_detail', slug=workshop.course.slug)

    # Check if the user has enough points
    if user.total_points < workshop.points_cost:
        messages.error(request, f"You do not have enough points to attend this workshop. Required: {workshop.points_cost}, Available: {user.total_points}.")
        return redirect('cms:course_detail', slug=workshop.course.slug)

    # Proceed to deduct points and create a Submission
    try:
        # Deduct points
        user.total_points -= workshop.points_cost
        user.save()

        # Create a Submission to record attendance
        Submission.objects.create(
            user=user,
            content_type=workshop_content_type,
            object_id=workshop.id,
            grade=100  # Assuming full marks for attendance
        )

        messages.success(request, f"You have successfully attended the workshop and spent {workshop.points_cost} points!")
    except Exception as e:
        messages.error(request, f"An error occurred while attending the workshop: {str(e)}")
        return redirect('cms:course_detail', slug=workshop.course.slug)

    return redirect('cms:course_detail', slug=workshop.course.slug)

@custom_login_required
def join_workshop(request, workshop_id):
    """
    View to redirect the user to the workshop's meeting link if they have attended.
    """
    workshop = get_object_or_404(Workshop, id=workshop_id)
    user = request.user

    # Get the ContentType for Workshop
    workshop_content_type = ContentType.objects.get_for_model(Workshop)

    # Check if the user has attended the workshop
    attended = Submission.objects.filter(
        user=user,
        content_type=workshop_content_type,
        object_id=workshop.id
    ).exists()

    if not attended:
        messages.error(request, "You need to attend the workshop before joining.")
        return redirect('cms:course_detail', slug=workshop.course.slug)

    if not workshop.meeting_link:
        messages.error(request, "No meeting link is available for this workshop.")
        return redirect('cms:course_detail', slug=workshop.course.slug)

    messages.info(request, "Redirecting you to the workshop meeting link.")
    return redirect(workshop.meeting_link)

@custom_login_required
def read_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    user = request.user

    # Check if the user has already read the article
    already_read = ArticleRead.objects.filter(user=user, article=article).exists()

    if already_read:
        messages.info(request, "You have already read this article.")
        return redirect('cms:course_detail', slug=article.course.slug)

    if request.method == 'POST':
        form = ArticleReadForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create ArticleRead record
                    points = article.points  # Assuming points are defined per article
                    ArticleRead.objects.create(
                        user=user,
                        article=article,
                        points_awarded=points
                    )
                    messages.success(request, f"Successfully read '{article.title}'. Earned {points} points.")
            except Exception as e:
                messages.error(request, f"An error occurred while reading the article: {str(e)}")
                return redirect('cms:course_detail', slug=article.course.slug)

            return redirect('cms:course_detail', slug=article.course.slug)
        else:
            messages.error(request, "Please correct the errors below in your article read confirmation.")
    else:
        form = ArticleReadForm()

    return render(request, 'cms/read_article_confirm.html', {'form': form, 'article': article})


@custom_login_required
def read_documentation(request, documentation_id):
    documentation = get_object_or_404(Documentation, id=documentation_id)
    user = request.user

    # Check if the user has already read the documentation
    already_read = DocumentationRead.objects.filter(user=user, documentation=documentation).exists()

    if already_read:
        messages.info(request, "You have already read this documentation.")
        return redirect('cms:course_detail', slug=documentation.course.slug)

    if request.method == 'POST':
        form = DocumentationReadForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create DocumentationRead record
                    points = documentation.points  # Assuming points are defined per documentation
                    DocumentationRead.objects.create(
                        user=user,
                        documentation=documentation,
                        points_awarded=points
                    )
                    messages.success(request, f"Successfully read '{documentation.title}'. Earned {points} points.")
            except Exception as e:
                messages.error(request, f"An error occurred while reading the documentation: {str(e)}")
                return redirect('cms:course_detail', slug=documentation.course.slug)

            return redirect('cms:course_detail', slug=documentation.course.slug)
        else:
            messages.error(request, "Please correct the errors below in your documentation read confirmation.")
    else:
        form = DocumentationReadForm()

    return render(request, 'cms/read_documentation_confirm.html', {'form': form, 'documentation': documentation})
