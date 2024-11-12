# cms/tests/test_views.py

from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.messages import get_messages
from datetime import timedelta

from cms.models import (
    Course, Challenge, Workshop, Submission, Enrollment,
    Assignment, Quiz, PointTransaction, Ranking
)
from ums.models import Profile

User = get_user_model()

class CMSViewsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the entire TestCase.
        """
        # Create users
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
            total_points=100
        )
        cls.other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',  # Ensure this email is unique
            password='otherpassword',
            total_points=50
        )
        
        # Adjust Ranking points if necessary
        cls.user.ranking.points = 100
        cls.user.ranking.save()

        cls.other_user.ranking.points = 50
        cls.other_user.ranking.save()
        
        # Create a course
        cls.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            proficiency_level='beginner'
        )

        # Enroll user in the course
        cls.enrollment = Enrollment.objects.create(user=cls.user, course=cls.course)

        # Create a challenge
        cls.challenge = Challenge.objects.create(
            title='Test Challenge',
            course=cls.course,
            points=50,
            date=timezone.now().date()
        )

        # Create a workshop
        cls.workshop = Workshop.objects.create(
            title='Test Workshop',
            course=cls.course,
            points_cost=30,
            duration=timedelta(hours=1, minutes=30),  # Example: 1.5 hours
            date_time=timezone.now() + timezone.timedelta(days=1),
            meeting_link='http://example.com/workshop'
        )

    def setUp(self):
        """
        Set up before each test method.
        """
        self.client = APIClient()
        # Authenticate the client
        response = self.client.post(reverse('pages:sign-in'), {
            'username': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.assertEqual(response.status_code, 200, "Authentication failed.")
        
        # Assuming the response contains a token
        # Adjust the key based on your authentication response
        self.token = response.data.get('token') or response.data.get('access')
        self.assertIsNotNone(self.token, "Token not found in authentication response.")

        # Set the token in the Authorization header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    # ----------------------------
    # Participate Challenge Tests
    # ----------------------------

    def test_participate_challenge_success(self):
        """
        Test that a user can successfully participate in a challenge.
        """
        url = reverse('cms:participate_challenge', args=[self.challenge.id])
        response = self.client.post(url)

        # Check redirection to challenge_detail
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('cms:challenge_detail', args=[self.challenge.id]))

        # Check that a Submission was created
        submission = Submission.objects.filter(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Challenge),
            object_id=self.challenge.id
        ).first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.grade, 100)

        # Check points updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_points, 150)  # 100 + 50

        # Check messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'You participated in the challenge and earned {self.challenge.points} points!')

    def test_participate_challenge_already_participated(self):
        """
        Test that a user cannot participate in the same challenge multiple times.
        """
        # Create an existing submission
        Submission.objects.create(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Challenge),
            object_id=self.challenge.id,
            grade=100
        )

        url = reverse('cms:participate_challenge', args=[self.challenge.id])
        response = self.client.post(url)

        # Check redirection to challenge_list
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('cms:challenge_list'))

        # Ensure no duplicate Submission
        submissions = Submission.objects.filter(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Challenge),
            object_id=self.challenge.id
        )
        self.assertEqual(submissions.count(), 1)

        # Check messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have already participated in this challenge.')

    # ----------------------------
    # Attend Workshop Tests
    # ----------------------------

    def test_attend_workshop_success(self):
        """
        Test that a user can successfully attend a workshop.
        """
        url = reverse('cms:attend_workshop', args=[self.workshop.id])
        response = self.client.get(url)

        # Check redirection to course_detail
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('cms:course_detail', args=[self.course.slug]))

        # Check that a Submission was created
        submission = Submission.objects.filter(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Workshop),
            object_id=self.workshop.id
        ).first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.grade, 100)

        # Check points deducted
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_points, 70)  # 100 - 30

        # Check messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"You have successfully attended the workshop and earned {self.workshop.points_cost} points!")

    def test_attend_workshop_already_attended(self):
        """
        Test that a user cannot attend the same workshop multiple times.
        """
        # Create an existing submission
        Submission.objects.create(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Workshop),
            object_id=self.workshop.id,
            grade=100
        )

        url = reverse('cms:attend_workshop', args=[self.workshop.id])
        response = self.client.get(url)

        # Check redirection to course_detail
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('cms:course_detail', args=[self.course.slug]))

        # Ensure no duplicate Submission
        submissions = Submission.objects.filter(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Workshop),
            object_id=self.workshop.id
        )
        self.assertEqual(submissions.count(), 1)

        # Check points not deducted again
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_points, 100)  # Points should remain the same

        # Check messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have already attended this workshop.")

    def test_attend_workshop_insufficient_points(self):
        """
        Test that a user cannot attend a workshop if they do not have enough points.
        """
        # Reduce user's points below workshop cost
        self.user.total_points = 20
        self.user.save()

        url = reverse('cms:attend_workshop', args=[self.workshop.id])
        response = self.client.get(url)

        # Check redirection to course_detail
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('cms:course_detail', args=[self.course.slug]))

        # Ensure no Submission was created
        submission = Submission.objects.filter(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Workshop),
            object_id=self.workshop.id
        ).first()
        self.assertIsNone(submission)

        # Check points remain unchanged
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_points, 20)

        # Check messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"You do not have enough points to attend this workshop. Required: {self.workshop.points_cost}, Available: {self.user.total_points}.")

    # ----------------------------
    # Join Workshop Tests
    # ----------------------------

    def test_join_workshop_success(self):
        """
        Test that a user can join a workshop after attending.
        """
        # First, attend the workshop
        Submission.objects.create(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Workshop),
            object_id=self.workshop.id,
            grade=100
        )

        url = reverse('cms:join_workshop', args=[self.workshop.id])
        response = self.client.get(url)

        # Check redirection to meeting link
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.workshop.meeting_link)

    def test_join_workshop_not_attended(self):
        """
        Test that a user cannot join a workshop without attending.
        """
        url = reverse('cms:join_workshop', args=[self.workshop.id])
        response = self.client.get(url)

        # Check redirection to course_detail
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('cms:course_detail', args=[self.course.slug]))

        # Check messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You need to attend the workshop before joining.")

    def test_join_workshop_no_meeting_link(self):
        """
        Test that a user cannot join a workshop if no meeting link is available.
        """
        # Remove the meeting link
        self.workshop.meeting_link = ''
        self.workshop.save()

        # Attend the workshop
        Submission.objects.create(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Workshop),
            object_id=self.workshop.id,
            grade=100
        )

        url = reverse('cms:join_workshop', args=[self.workshop.id])
        response = self.client.get(url)

        # Check redirection to course_detail
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('cms:course_detail', args=[self.course.slug]))

        # Check messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "No meeting link is available for this workshop.")

    # ----------------------------
    # Challenge Detail View Tests
    # ----------------------------

    def test_challenge_detail_registered_true(self):
        """
        Test that the challenge detail view shows 'Already Registered' for users who have participated.
        """
        # Create a submission
        Submission.objects.create(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Challenge),
            object_id=self.challenge.id,
            grade=100
        )

        url = reverse('cms:challenge_detail', args=[self.challenge.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Already Registered")
        self.assertNotContains(response, "Register")

    def test_challenge_detail_registered_false(self):
        """
        Test that the challenge detail view shows 'Register' for users who have not participated.
        """
        url = reverse('cms:challenge_detail', args=[self.challenge.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register")
        self.assertNotContains(response, "Already Registered")

    def test_challenge_detail_not_enrolled(self):
        """
        Test that accessing a challenge detail page for a course the user is not enrolled in shows access denied.
        """
        # Create another course and challenge
        other_course = Course.objects.create(
            title='Other Course',
            slug='other-course',
            proficiency_level='intermediate'
        )
        other_challenge = Challenge.objects.create(
            title='Other Challenge',
            course=other_course,
            points=60,
            date=timezone.now().date()
        )

        url = reverse('cms:challenge_detail', args=[other_challenge.id])
        response = self.client.get(url)

        # Check access denied template
        self.assertEqual(response.status_code, 200)  # Assuming access_denied.html is rendered with status 200
        self.assertTemplateUsed(response, 'cms/access_denied.html')
        self.assertContains(response, 'Access Denied')  # Assuming access_denied.html contains this text

    # ----------------------------
    # Authentication Tests
    # ----------------------------

    def test_participate_challenge_unauthenticated(self):
        """
        Test that an unauthenticated user cannot participate in a challenge.
        """
        self.client.credentials()  # Remove authentication
        url = reverse('cms:participate_challenge', args=[self.challenge.id])
        response = self.client.post(url)

        # Should redirect to login
        login_url = reverse('pages:sign-in') + f"?next={reverse('cms:participate_challenge', args=[self.challenge.id])}"
        self.assertRedirects(response, login_url)

    def test_attend_workshop_unauthenticated(self):
        """
        Test that an unauthenticated user cannot attend a workshop.
        """
        self.client.credentials()  # Remove authentication
        url = reverse('cms:attend_workshop', args=[self.workshop.id])
        response = self.client.get(url)

        # Should redirect to login
        login_url = reverse('pages:sign-in') + f"?next={reverse('cms:attend_workshop', args=[self.workshop.id])}"
        self.assertRedirects(response, login_url)

    def test_join_workshop_unauthenticated(self):
        """
        Test that an unauthenticated user cannot join a workshop.
        """
        self.client.credentials()  # Remove authentication
        url = reverse('cms:join_workshop', args=[self.workshop.id])
        response = self.client.get(url)

        # Should redirect to login
        login_url = reverse('pages:sign-in') + f"?next={reverse('cms:join_workshop', args=[self.workshop.id])}"
        self.assertRedirects(response, login_url)

    # ----------------------------
    # Additional Tests
    # ----------------------------

    def test_join_workshop_invalid_workshop_id(self):
        """
        Test that joining a workshop with an invalid ID returns a 404.
        """
        invalid_id = self.workshop.id + 999
        url = reverse('cms:join_workshop', args=[invalid_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_participate_challenge_invalid_challenge_id(self):
        """
        Test that participating in a challenge with an invalid ID returns a 404.
        """
        invalid_id = self.challenge.id + 999
        url = reverse('cms:participate_challenge', args=[invalid_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_attend_workshop_invalid_workshop_id(self):
        """
        Test that attending a workshop with an invalid ID returns a 404.
        """
        invalid_id = self.workshop.id + 999
        url = reverse('cms:attend_workshop', args=[invalid_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
