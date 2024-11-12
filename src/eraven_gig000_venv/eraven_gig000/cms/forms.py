# cms/forms.py

from django import forms
from .models import Submission, Assignment, Quiz, Challenge, Workshop, Session
from django.contrib.contenttypes.models import ContentType

class SubmissionForm(forms.ModelForm):
    # Dropdowns for selecting specific content type instances
    assignment = forms.ModelChoiceField(
        queryset=Assignment.objects.all(),
        required=False,
        label="Assignment"
    )
    quiz = forms.ModelChoiceField(
        queryset=Quiz.objects.all(),
        required=False,
        label="Quiz"
    )
    challenge = forms.ModelChoiceField(
        queryset=Challenge.objects.all(),
        required=False,
        label="Challenge"
    )
    workshop = forms.ModelChoiceField(
        queryset=Workshop.objects.all(),
        required=False,
        label="Workshop"
    )
    session = forms.ModelChoiceField(
        queryset=Session.objects.all(),
        required=False,
        label="Session"
    )

    class Meta:
        model = Submission
        fields = ['user', 'grade', 'assignment', 'quiz', 'challenge', 'workshop', 'session']
        widgets = {
            'user': forms.HiddenInput(),  # Hide the user field if it's set automatically
        }

    def clean(self):
        cleaned_data = super().clean()

        # Extract all content type fields
        assignment = cleaned_data.get('assignment')
        quiz = cleaned_data.get('quiz')
        challenge = cleaned_data.get('challenge')
        workshop = cleaned_data.get('workshop')
        session = cleaned_data.get('session')

        # Count how many content type fields are filled
        selected_fields = [
            field for field in [assignment, quiz, challenge, workshop, session] if field is not None
        ]

        if len(selected_fields) == 0:
            raise forms.ValidationError("Please select one type of content for the submission.")
        elif len(selected_fields) > 1:
            raise forms.ValidationError("Please select only one type of content for the submission.")

        # Determine which content type is selected
        content_object = selected_fields[0]
        content_type = ContentType.objects.get_for_model(content_object.__class__)

        # Set `content_type` and `object_id` in the instance
        self.instance.content_type = content_type
        self.instance.object_id = content_object.id

        return cleaned_data

class BaseSubmissionForm(forms.ModelForm):
    """
    A base form for submitting different types of content.
    """
    content = forms.ModelChoiceField(
        queryset=None,
        required=True,
        label="Select Content"
    )

    class Meta:
        model = Submission
        fields = ['grade']  # Include 'grade' only if users should set it during submission

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with a specific queryset for the 'content' field.
        """
        content_queryset = kwargs.pop('content_queryset', None)
        super().__init__(*args, **kwargs)
        if content_queryset is not None:
            self.fields['content'].queryset = content_queryset

    def save(self, commit=True, user=None):
        """
        Save the submission, associating it with the selected content and user.
        """
        submission = super().save(commit=False)
        content_object = self.cleaned_data['content']
        submission.content_object = content_object  # Automatically sets content_type and object_id

        if user:
            submission.user = user  # Associate the submission with the current user

        if commit:
            submission.save()
        return submission


class AssignmentSubmissionForm(BaseSubmissionForm):
    """
    Form for submitting an Assignment.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, content_queryset=Assignment.objects.all())
        self.fields['content'].label = "Select Assignment"


class QuizSubmissionForm(BaseSubmissionForm):
    """
    Form for submitting a Quiz.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, content_queryset=Quiz.objects.all())
        self.fields['content'].label = "Select Quiz"


class ChallengeSubmissionForm(BaseSubmissionForm):
    """
    Form for submitting a Challenge.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, content_queryset=Challenge.objects.all())
        self.fields['content'].label = "Select Challenge"


class WorkshopSubmissionForm(BaseSubmissionForm):
    """
    Form for submitting a Workshop.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, content_queryset=Workshop.objects.all())
        self.fields['content'].label = "Select Workshop"


class ArticleReadForm(forms.Form):
    """
    Form to confirm reading an article.
    """
    confirm = forms.BooleanField(
        required=True,
        label="Confirm that you have read this article."
    )


class DocumentationReadForm(forms.Form):
    """
    Form to confirm reading documentation.
    """
    confirm = forms.BooleanField(
        required=True,
        label="Confirm that you have read this documentation."
    )
