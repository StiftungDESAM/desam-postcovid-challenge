from django.db import models
import pandas as pd
from typing import List

from authentication.models import CustomUser

# Create your models here.
class Purpose(models.TextChoices):
    FEASIBILITY_CHECK = 'FEASIBILITY_CHECK', 'FEASIBILITY_CHECK'
    PILOT_STUDY = 'PILOT_STUDY', 'PILOT_STUDY'
    DATA_ANALYSIS = 'DATA_ANALYSIS', 'DATA_ANALYSIS'
    DATA_COLLECTION = 'DATA_COLLECTION', 'DATA_COLLECTION'
    INTERVENTION_RESEARCH = 'INTERVENTION_RESEARCH', 'INTERVENTION_RESEARCH'

class Study(models.Model):
    id = models.AutoField(primary_key=True)
    submitter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="submitted_studies")
    submission_date = models.DateTimeField(auto_now_add=True)
    name = models.TextField()
    purpose = models.CharField(max_length=50, choices=Purpose.choices)
    date_start = models.DateField()
    date_end = models.DateField()
    drks_id = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    @property
    def ontology_review(self):
        from reviewer.models import UploadTypeChoices
        return self.reviews.get(upload_type = UploadTypeChoices.UPLOAD_ONTOLOGY.value)
    
    @property
    def data_review(self):
        from reviewer.models import UploadTypeChoices
        return self.reviews.get(upload_type = UploadTypeChoices.UPLOAD_DATA.value)

class CodeBook(models.Model):
    study = models.ForeignKey(Study, related_name='codebooks', on_delete=models.CASCADE)
    name = models.TextField()

    def __str__(self):
        return self.name

class CodeBookColumn(models.Model):
    class Meta:
        ordering = ["codebook", "idx"]
        
    codebook = models.ForeignKey(CodeBook, related_name='columns', on_delete=models.CASCADE)
    idx = models.IntegerField()
    header = models.TextField()
    assigned_meta_tag = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Row in {self.codebook.name}"
    
class CodeBookRow(models.Model):
    codebook = models.ForeignKey(CodeBook, related_name='rows', on_delete=models.CASCADE)
    cells = models.JSONField()  
    row_id = models.IntegerField()
    assigned_item_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Row in {self.codebook.name}"
