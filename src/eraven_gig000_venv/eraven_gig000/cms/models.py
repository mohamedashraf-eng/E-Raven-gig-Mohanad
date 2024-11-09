# cms/models.py

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = settings.AUTH_USER_MODEL


# =======================
# CMS Models
# =======================

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ContentBase(models.Model):
    PROFICIENCY_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, editable=False)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_contents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(
        Category,
        related_name='%(class)s_contents'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='%(class)s_contents',
        blank=True
    )
    proficiency_level = models.CharField(
        max_length=50,
        choices=PROFICIENCY_LEVEL_CHOICES
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    syllabus = models.TextField()
    prerequisites = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    proficiency_level = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='articles', default=1)  # Default value for migration
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Video(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video_url = models.URLField()
    description = models.TextField()
    proficiency_level = models.CharField(max_length=50)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos', default=1)  # Default value for migration
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Post(ContentBase):
    slug = models.SlugField(unique=True, blank=True)  # Ensure slug is defined
    short_content = models.TextField()
    content = models.TextField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Documentation(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    file = models.FileField(upload_to='docs/')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='documentations', default=1)  # Default value for migration
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')  # Prevent duplicate enrollments

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"
    
# =======================
# LMS Models
# =======================

class Assignment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments',
        default=1  # Default value for migration
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Quiz(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes',
        default=1  # Default value for migration
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Challenge(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField(default=timezone.now)
    points = models.PositiveIntegerField(default=10)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='challenges', default=1)  # Default value for migration
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('title', 'date')

    def __str__(self):
        return f"{self.title} on {self.date}"


class Submission(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        null=True,
        blank=True
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='submissions',
        null=True,
        blank=True
    )
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )

    def __str__(self):
        if self.assignment:
            return f"Submission by {self.user.username} for {self.assignment.title}"
        elif self.quiz:
            return f"Submission by {self.user.username} for {self.quiz.title}"
        return f"Submission by {self.user.username}"


class UserProgress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progresses'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='progresses',
        default=1  # Default value for migration
    )
    completed = models.BooleanField(default=False)
    progress_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} - {self.course.title} Progress"


class PointTransaction(models.Model):
    POINTS_CHOICES = [
        ('earn', 'Earned'),
        ('spend', 'Spent'),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='point_transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=POINTS_CHOICES)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} {self.points} points"


class Ranking(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ranking')
    points = models.IntegerField(default=0)
    rank = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - Rank {self.rank} - {self.points} Points"

    class Meta:
        ordering = ['-points']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_rank()

    def update_rank(self):
        rankings = Ranking.objects.order_by('-points')
        for idx, ranking in enumerate(rankings, start=1):
            ranking.rank = idx
            super(Ranking, ranking).save()


# =======================
# Signals
# =======================

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_ranking(sender, instance, created, **kwargs):
    if created:
        Ranking.objects.create(user=instance)
