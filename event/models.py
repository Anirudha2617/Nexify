from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from django.contrib.auth.models import User

class Form(models.Model):
    created_by = models.ForeignKey(
        User,  # Use app_label.ModelName as a string
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
        related_name='created_forms'
    )
    form_type = models.CharField(max_length=40, default  = 'miscillineous')
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='form_images/', blank=True, null=True)  # Store image file path

    def __str__(self):
        return self.title

class Question(models.Model):
    TEXT = 'TEXT'
    MULTIPLE_CHOICE = 'MC'
    SHORT_ANSWER = 'SA'
    LONG_ANSWER = 'LA'
    DROP_DOWN = 'DD'
    DATE_TIME = 'DT'
    IMAGE_TYPE ='IMG'

    QUESTION_TYPES = [
        (TEXT, 'Text'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (SHORT_ANSWER, 'Short Answer'),
        (LONG_ANSWER, 'Long Answer'),
        (DROP_DOWN, 'Dropdown'),
        (DATE_TIME, 'Date and Time'),
        (IMAGE_TYPE, 'Image'),
    ]

    form = models.ForeignKey(Form, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    question_type = models.CharField(choices=QUESTION_TYPES, max_length=20, default=TEXT)
    choices = models.TextField(blank=True, null=True)  # Store choices as comma-separated values
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)  # Store image file path

    def __str__(self):
        return self.text

    def get_choices(self):
        """Utility method to get choices as a list for multiple choice or dropdown questions."""
        if self.question_type in [self.MULTIPLE_CHOICE, self.DROP_DOWN] and self.choices:
            return self.choices.split(',')
        return []
    
class Response(models.Model):
    form = models.ForeignKey(Form, related_name='responses', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Response to {self.form.title} on {self.created_at}'

class Answer(models.Model):
    response = models.ForeignKey(Response, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)  # Store the answer as text, regardless of question type
    answer_image = models.ImageField(upload_to='uploads/', blank=True, null=True)  # New field for images

    def __str__(self):
        return f'Answer to {self.question.text}'

    def clean(self):
        """Custom validation to ensure answer matches question type."""
        if self.question.question_type in [Question.MULTIPLE_CHOICE, Question.DROP_DOWN]:
            if self.answer_text not in self.question.get_choices():
                raise ValidationError(f"Invalid choice for {self.question.question_type} question.")
        elif self.question.question_type == Question.DATE_TIME:
            try:
                datetime.strptime(self.answer_text, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValidationError("Invalid date and time format. Use 'YYYY-MM-DD HH:MM:SS' format.")


class ExtraDetails(models.Model):
    Model = models.ForeignKey(
        Form, 
        related_name='extradetails', 
        on_delete=models.CASCADE,
        default=None,
        null=False,
        blank=False,)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='form_images/', blank=True, null=True)  # Store image file path

    def __str__(self):
        return self.title

class ExtraQuestion(models.Model):
    TEXT = 'TEXT'
    SINGLE_CHOICE = 'SC'
    MULTIPLE_CHOICE = 'MC'
    SHORT_ANSWER = 'SA'
    LONG_ANSWER = 'LA'
    DROP_DOWN = 'DD'
    DATE_TIME = 'DT'
    IMAGE_TYPE ='IMG'

    QUESTION_TYPES = [
        (TEXT, 'Text'),
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (SHORT_ANSWER, 'Short Answer'),
        (LONG_ANSWER, 'Long Answer'),
        (DROP_DOWN, 'Dropdown'),
        (DATE_TIME, 'Date and Time'),
        (IMAGE_TYPE, 'Image'),
    ]

    form = models.ForeignKey(ExtraDetails, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    question_type = models.CharField(choices=QUESTION_TYPES, max_length=20, default=TEXT)
    choices = models.TextField(blank=True, null=True)  # Store choices as comma-separated values
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)  # Store image file path

    def __str__(self):
        return self.text

    def get_choices(self):
        """Utility method to get choices as a list for multiple choice or dropdown questions."""
        if self.question_type in [self.MULTIPLE_CHOICE, self.DROP_DOWN] and self.choices:
            return self.choices.split(',')
        return []
    
class ExtraResponse(models.Model):
    form = models.ForeignKey(ExtraDetails, related_name='responses', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Response to {self.form.title} on {self.created_at}'

class ExtraAnswer(models.Model):
    response = models.ForeignKey(ExtraResponse, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(ExtraQuestion, related_name='answers', on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)  # Store the answer as text, regardless of question type
    answer_image = models.ImageField(upload_to='uploads/', blank=True, null=True)  # New field for images

    def __str__(self):
        return f'Answer to {self.question.text}'

    def clean(self):
        """Custom validation to ensure answer matches question type."""
        if self.question.question_type in [ExtraQuestion.MULTIPLE_CHOICE, ExtraQuestion.DROP_DOWN]:
            if self.answer_text not in self.question.get_choices():
                raise ValidationError(f"Invalid choice for {self.question.question_type} question.")
        elif self.question.question_type == ExtraQuestion.DATE_TIME:
            try:
                datetime.strptime(self.answer_text, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValidationError("Invalid date and time format. Use 'YYYY-MM-DD HH:MM:SS' format.")