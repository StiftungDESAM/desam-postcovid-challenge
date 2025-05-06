from django.db import models
from enum import Enum
from authentication.models import CustomUser
from study.models import Study

class StatusChoices(Enum):
    STATUS_OPEN = "OPEN"
    STATUS_ASSIGNED = "ASSIGNED"
    STATUS_MODIFICATION_NEEDED = "MODIFICATION_NEEDED"
    STATUS_DECLINED = "DECLINED"
    STATUS_ACCEPTED = "ACCEPTED"

    @classmethod
    def choices(cls):
        return [(status.value, status.value.replace("_", " ").title()) for status in cls]
    
class UploadTypeChoices(Enum):
    UPLOAD_DATA = "UPLOAD_DATA"
    UPLOAD_ONTOLOGY = "UPLOAD_ONTOLOGY"

    @classmethod
    def choices(cls):
        return [(choice.value, choice.value.replace("_", " ").title()) for choice in cls]
    

class Review(models.Model):

    class Meta:
        app_label = 'reviewer'

    id = models.AutoField(primary_key=True)
    submitter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="submitted_reviews")
    submission_date = models.DateTimeField()
    reviewer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_reviews")
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="reviews", null=True,blank=True)
    submission_status = models.CharField(
        max_length=30,
        choices=StatusChoices.choices(), 
        default=StatusChoices.STATUS_OPEN.value  # Default status is 'OPEN'
    )
    upload_type = models.CharField(
        max_length=30,
        choices=UploadTypeChoices.choices(),
        default=UploadTypeChoices.UPLOAD_ONTOLOGY.value  
    )

    def __str__(self):
        return f"Review ID: {self.id}, Submitter: {self.submitter.email}, Status: {self.submission_status}"
            
class ReviewDetails(models.Model):
    class Meta:
        app_label = 'reviewer'
    id = models.AutoField(primary_key=True)
    reviewer_details = models.OneToOneField('Review', on_delete=models.CASCADE, related_name='details') 
    status = models.CharField(max_length=20, choices=[
        ("MODIFICATION_NEEDED", "MODIFICATION_NEEDED"),
        ("DECLINED", "DECLINED"),
        ("ACCEPTED", "ACCEPTED"),
    ], null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    modified_ontology = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Submission ID: {self.id}, Review ID: {self.reviewer_details.id}"

class Feedback(models.Model):
    review = models.OneToOneField('Review', on_delete=models.CASCADE, related_name="feedback")
    
    def __str__(self):
        return f"Feedback ID: {self.id} for Review ID: {self.review.id}"    
