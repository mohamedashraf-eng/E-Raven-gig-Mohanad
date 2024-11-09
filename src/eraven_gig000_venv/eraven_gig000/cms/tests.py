# cms/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import (
    Course, Assignment, Quiz, Challenge,
    Submission, UserProgress, PointTransaction, Ranking
)
from django.utils import timezone
from django.urls import reverse

User = get_user_model()

class LMSModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.course = Course.objects.create(
            title='English Grammar',
            author=self.user,
            proficiency_level='beginner',
            description='Learn the basics of English grammar.',
            syllabus='Chapter 1: Nouns, Chapter 2: Verbs'
        )
        self.assignment = Assignment.objects.create(
            course=self.course,
            title='Nouns Assignment',
            description='Write 10 sentences using nouns.',
            due_date=timezone.now() + timezone.timedelta(days=7)
        )
        self.quiz = Quiz.objects.create(
            course=self.course,
            title='Nouns Quiz',
            description='Test your knowledge of nouns.'
        )
        self.challenge = Challenge.objects.create(
            title='Daily Vocabulary',
            description='Learn 5 new words today.',
            points=5,
            date=timezone.now().date()
        )
        self.ranking = self.user.ranking

    def test_assignment_creation(self):
        self.assertEqual(self.assignment.title, 'Nouns Assignment')
        self.assertEqual(self.assignment.course, self.course)

    def test_quiz_creation(self):
        self.assertEqual(self.quiz.title, 'Nouns Quiz')
        self.assertEqual(self.quiz.course, self.course)

    def test_challenge_creation(self):
        self.assertEqual(self.challenge.title, 'Daily Vocabulary')
        self.assertEqual(self.challenge.points, 5)

    def test_submission_creation(self):
        submission = Submission.objects.create(
            user=self.user,
            assignment=self.assignment,
            content='This is my assignment submission.',
            grade=85
        )
        self.assertEqual(submission.user, self.user)
        self.assertEqual(submission.assignment, self.assignment)
        self.assertEqual(submission.grade, 85)

    def test_user_progress_creation(self):
        user_progress = UserProgress.objects.create(
            user=self.user,
            course=self.course,
            progress_percentage=50.0,
            completed=False
        )
        self.assertEqual(user_progress.user, self.user)
        self.assertEqual(user_progress.course, self.course)
        self.assertEqual(user_progress.progress_percentage, 50.0)

    def test_point_transaction_creation(self):
        transaction = PointTransaction.objects.create(
            user=self.user,
            transaction_type='earn',
            points=10,
            description='Earned points for completing an assignment.'
        )
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.points, 10)
        self.assertEqual(transaction.transaction_type, 'earn')

    def test_ranking_creation(self):
        self.assertEqual(self.ranking.user, self.user)
        self.assertEqual(self.ranking.points, 0)
        self.assertEqual(self.ranking.rank, 1)

class LMSViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.course = Course.objects.create(
            title='English Grammar',
            author=self.user,
            proficiency_level='beginner',
            description='Learn the basics of English grammar.',
            syllabus='Chapter 1: Nouns, Chapter 2: Verbs'
        )
        self.client.login(username='testuser', password='password')

    def test_assignment_list_view(self):
        url = reverse('cms:assignment_list', kwargs={'course_slug': self.course.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.title)

    def test_participate_challenge_view(self):
        challenge = Challenge.objects.create(
            title='Daily Vocabulary',
            description='Learn 5 new words today.',
            points=5,
            date=timezone.now().date()
        )
        url = reverse('cms:participate_challenge', kwargs={'challenge_id': challenge.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect after participation
        self.user.ranking.refresh_from_db()
        self.assertEqual(self.user.ranking.points, 5)
