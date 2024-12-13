# from django.db import models
# from django.core.exceptions import ValidationError
# from datetime import datetime
# from django.contrib.auth.models import User
# from club.models import ClubDetails
# from ckeditor.fields import RichTextField 



# class Form(models.Model):
#     created_by = models.ForeignKey(
#         User,  # Use app_label.ModelName as a string
#         on_delete=models.CASCADE,
#         default=None,
#         null=True,
#         blank=True,
#         related_name='created_forms'
#     )
#     club = models.ForeignKey(ClubDetails, on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='forms')
#     form_type = models.CharField(max_length=40, default  = 'miscillineous')
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     image = models.ImageField(upload_to='form_images/', blank=True, null=True)  # Store image file path
#     is_public = models.BooleanField(default=False)

#     def __str__(self):
#         return self.title

# class Question(models.Model):
#     TEXT = 'TEXT'
#     MULTIPLE_CHOICE = 'MC'
#     SHORT_ANSWER = 'SA'
#     LONG_ANSWER = 'LA'
#     DROP_DOWN = 'DD'
#     DATE_TIME = 'DT'
#     IMAGE_TYPE ='IMG'

#     QUESTION_TYPES = [
#         (TEXT, 'Text'),
#         (MULTIPLE_CHOICE, 'Multiple Choice'),
#         (SHORT_ANSWER, 'Short Answer'),
#         (LONG_ANSWER, 'Long Answer'),
#         (DROP_DOWN, 'Dropdown'),
#         (DATE_TIME, 'Date and Time'),
#         (IMAGE_TYPE, 'Image'),
#     ]

#     form = models.ForeignKey(Form, related_name='questions', on_delete=models.CASCADE)
#     text = models.CharField(max_length=255)
#     question_type = models.CharField(choices=QUESTION_TYPES, max_length=20, default=TEXT)
#     choices = models.TextField(blank=True, null=True)  # Store choices as comma-separated values
#     image = models.ImageField(upload_to='question_images/', blank=True, null=True)  # Store image file path

#     def __str__(self):
#         return self.text

#     def get_choices(self):
#         """Utility method to get choices as a list for multiple choice or dropdown questions."""
#         if self.question_type in [self.MULTIPLE_CHOICE, self.DROP_DOWN] and self.choices:
#             return self.choices.split(',')
#         return []
    
# class Response(models.Model):
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='created_by')
#     created_at = models.DateTimeField(auto_now_add=True)
#     form = models.ForeignKey(Form, related_name='responses', on_delete=models.CASCADE , null=True , blank=True  )

#     def __str__(self):
#         return f'Response to {self.form.title} on {self.created_at}'
    

# class Answer(models.Model):
#     response = models.ForeignKey(Response, related_name='answers', on_delete=models.CASCADE)
#     question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
#     answer_text = models.TextField(blank=True, null=True)  # Store the answer as text, regardless of question type
#     answer_image = models.ImageField(upload_to='uploads/', blank=True, null=True)  # New field for images

#     def __str__(self):
#         return f'Answer to {self.question.text}'

#     def clean(self):
#         """Custom validation to ensure answer matches question type."""
#         if self.question.question_type in [Question.MULTIPLE_CHOICE, Question.DROP_DOWN]:
#             if self.answer_text not in self.question.get_choices():
#                 raise ValidationError(f"Invalid choice for {self.question.question_type} question.")
#         elif self.question.question_type == Question.DATE_TIME:
#             try:
#                 datetime.strptime(self.answer_text, '%Y-%m-%d %H:%M:%S')
#             except ValueError:
#                 raise ValidationError("Invalid date and time format. Use 'YYYY-MM-DD HH:MM:SS' format.")

# class ExtraDetails(models.Model):
#     Model = models.ForeignKey(
#         Form, 
#         related_name='extradetails', 
#         on_delete=models.CASCADE,
#         default=None,
#         null=False,
#         blank=False,)
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     image = models.ImageField(upload_to='form_images/', blank=True, null=True)  # Store image file path

#     def __str__(self):
#         return self.title

# class ExtraQuestion(models.Model):
#     TEXT = 'TEXT'
#     SINGLE_CHOICE = 'SC'
#     MULTIPLE_CHOICE = 'MC'
#     SHORT_ANSWER = 'SA'
#     LONG_ANSWER = 'LA'
#     DROP_DOWN = 'DD'
#     DATE_TIME = 'DT'
#     IMAGE_TYPE ='IMG'

#     QUESTION_TYPES = [
#         (TEXT, 'Text'),
#         (SINGLE_CHOICE, 'Single Choice'),
#         (MULTIPLE_CHOICE, 'Multiple Choice'),
#         (SHORT_ANSWER, 'Short Answer'),
#         (LONG_ANSWER, 'Long Answer'),
#         (DROP_DOWN, 'Dropdown'),
#         (DATE_TIME, 'Date and Time'),
#         (IMAGE_TYPE, 'Image'),
#     ]

#     form = models.ForeignKey(ExtraDetails, related_name='questions', on_delete=models.CASCADE)
#     text = models.CharField(max_length=255)
#     question_type = models.CharField(choices=QUESTION_TYPES, max_length=20, default=TEXT)
#     choices = models.TextField(blank=True, null=True)  # Store choices as comma-separated values
#     image = models.ImageField(upload_to='question_images/', blank=True, null=True)  # Store image file path

#     def __str__(self):
#         return self.text

#     def get_choices(self):
#         """Utility method to get choices as a list for multiple choice or dropdown questions."""
#         if self.question_type in [self.MULTIPLE_CHOICE, self.DROP_DOWN] and self.choices:
#             return self.choices.split(',')
#         return []
    
# class ExtraResponse(models.Model):
#     form = models.ForeignKey(ExtraDetails, related_name='responses', on_delete=models.CASCADE)
#     response = models.ForeignKey(Response, related_name='extra_responses', on_delete=models.CASCADE ,blank = True , null = True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'Response to {self.form.title} on {self.created_at}'

# class ExtraAnswer(models.Model):
#     response = models.ForeignKey(ExtraResponse, related_name='answers', on_delete=models.CASCADE)
#     question = models.ForeignKey(ExtraQuestion, related_name='answers', on_delete=models.CASCADE)
#     answer_text = models.TextField(blank=True, null=True)  # Store the answer as text, regardless of question type
#     answer_image = models.ImageField(upload_to='uploads/', blank=True, null=True)  # New field for images

#     def __str__(self):
#         return f'Answer to {self.question.text}'

#     def clean(self):
#         """Custom validation to ensure answer matches question type."""
#         if self.question.question_type in [ExtraQuestion.MULTIPLE_CHOICE, ExtraQuestion.DROP_DOWN]:
#             if self.answer_text not in self.question.get_choices():
#                 raise ValidationError(f"Invalid choice for {self.question.question_type} question.")
#         elif self.question.question_type == ExtraQuestion.DATE_TIME:
#             try:
#                 datetime.strptime(self.answer_text, '%Y-%m-%d %H:%M:%S')
#             except ValueError:
#                 raise ValidationError("Invalid date and time format. Use 'YYYY-MM-DD HH:MM:SS' format.")

# class Registration_details(models.Model):
#     INDIVIDUAL  = "individual"
#     GROUP = "group"
#     PUBLIC = "Public"
#     CLUB = 'Clubs'
#     INVITED = 'Invited'

#     PARTICIPATION_TYPE = [
#         (INDIVIDUAL, 'Individual'),
#         (GROUP, 'Group'),
#     ]

#     VISIBILITY_TYPE = [
#         (PUBLIC, 'Public'),
#         (CLUB, 'Clubs'),
#         (INVITED, 'Invited')
#     ]
#     response = models.ForeignKey(Response, related_name='registration_details', on_delete=models.CASCADE ,blank = True , null = True)

#     form = models.ForeignKey(Form, related_name='registration_details', on_delete=models.CASCADE ,blank = True , null = True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='registration_details')

#     visibility = models.CharField(choices=VISIBILITY_TYPE, max_length=20, default=INDIVIDUAL)
#     compulsary = models.BooleanField(default=False)
#     invited_users = models.ManyToManyField(User, related_name='invited_events', blank=True)
#     accepted_users = models.ManyToManyField(User, related_name='accepted_events', blank=True)
#     rejected_users = models.ManyToManyField(User, related_name='rejected_events', blank=True)
    
#     invited_club = models.ManyToManyField(ClubDetails, blank=True, related_name='events')


#     platform = models.BooleanField()
#     participation_type = models.CharField(choices=PARTICIPATION_TYPE, max_length=20, default=INDIVIDUAL)
#     minimum_members = models.IntegerField(default=1)
#     maximum_members = models.IntegerField(default=1)
#     registration_start = models.DateTimeField(blank = False , null = False , default = datetime.now())
#     registration_end = models.DateTimeField(blank = False , null = False )
#     number_of_registration = models.IntegerField(blank=True, null=True)

# class Notification(models.Model):
#     # Notification types
#     INFO = 'info'
#     WARNING = 'warning'
#     ERROR = 'error'
#     SUCCESS = 'success'

#     NOTIFICATION_TYPES = [
#         (INFO, 'Info'),
#         (WARNING, 'Warning'),
#         (ERROR, 'Error'),
#         (SUCCESS, 'Success'),
#     ]

#     # Fields
#     sent_from = models.ForeignKey(User, related_name = 'form_sent_notifications', on_delete=models.CASCADE )
#     event = models.ForeignKey(Registration_details, related_name = 'form_notifications', on_delete=models.CASCADE , null =True )
#     user = models.ForeignKey(User, related_name = 'event_notifications', on_delete=models.CASCADE )
#     title = models.CharField(max_length=255)
#     message = models.TextField()
#     notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default=INFO)
#     is_read = models.BooleanField(default=False)
#     status = models.BooleanField(null= True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Notification for {self.user.username}: {self.title}: {self.status}"

#     # Methods
#     def mark_as_read(self):
#         self.is_read = True
#         self.save()

#     def mark_as_unread(self):
#         self.is_read = False
#         self.save()

#     @classmethod
#     def create_notification(cls, user, title, message, sent_from, event, notification_type=INFO ):
#         return cls.objects.create(
#             user=user,
#             title=title,
#             message=message,
#             notification_type=notification_type,
#             sent_from=sent_from,
#             event = event,
#         )

#     @classmethod
#     def get_unread_notifications(cls, user):
#          return cls.objects.filter(user=user, is_read=False)


#     @classmethod
#     def get_all_notifications(cls, user):
#          return cls.objects.filter(user=user)

#     @classmethod
#     def mark_all_as_read(cls, user):
#         cls.objects.filter(user=user, is_read=False).update(is_read=True)

#     @classmethod
#     def get_rejectednotification(cls, sent_by,sent_to,event ):
#         a = cls.objects.filter(sent_from=sent_by, event=event, user = sent_to , status = False)
#         from django.db.models import Q
#         a = a.filter(Q(status=False) | Q(status__isnull=True))
#         return a
    
#     @classmethod
#     def get_notification(cls, sent_by,sent_to,event ):
#         a = cls.objects.filter(sent_from=sent_by, event=event, user = sent_to )
#         return a

#     def perform_action(self , status):
#         """
#         Perform action based on the `action_button` value.
#         """
#         self.status = status
#         self.mark_as_read()
#         if self.status:
#             return self.action_true()
#         else:
#             return self.action_false()

#     def action_true(self):
#         # Action when `action_button` is True
#         self.event.invited_users.remove(self.user)
#         self.event.accepted_users.add(self.user)
#         self.save()

#     def action_false(self):
#         # Action when `action_button` is False
#         self.event.invited_users.remove(self.user)
#         self.event.rejected_users.add(self.user)
#         print("User poppeed......")
