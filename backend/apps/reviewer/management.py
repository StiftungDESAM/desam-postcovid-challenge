from reviewer.models import Feedback, Review,StatusChoices,UploadTypeChoices,ReviewDetails
from django.utils import timezone

def create_review_process(current_user,diffrdf):
        # Create new review process in DB
    review_instance = Review.objects.create(
        submitter=current_user,
        submission_date=timezone.now(),
        study=None,
        submission_status=StatusChoices.STATUS_OPEN.value,
        upload_type=UploadTypeChoices.UPLOAD_ONTOLOGY.value 
    )
    
    ReviewDetails.objects.create(
        reviewer_details=review_instance,
        status=None, 
        comment=None,
        modified_ontology=diffrdf,
    )
    
    # Create new feedback  in DB
    Feedback.objects.create(review=review_instance)
    