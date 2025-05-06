from api.transactions import TransactionRouter

from ninja import Body
from ninja.errors import HttpError
from neomodel import db
from django.shortcuts import get_object_or_404

from api import schema
from api.permissions import PermissionChecker
from reviewer.models import Review, ReviewDetails, StatusChoices, Feedback, UploadTypeChoices
from authentication.models import CustomUser
from knowledge import graph_functions
from knowledge.models import load_all_knowledge_node_classes
from graph_migrations.studies import load_migrations
from ontology.importer import import_rdf
from ontology.data_requests import get_codebooks_for_rdf
from ontology.diff import entities_to_rdf

import logging
logger = logging.getLogger(__name__)

router = TransactionRouter()

def assign_reviewer_logic(reviewID: int, email: str, expected_type: str):
    review = get_object_or_404(Review, id=reviewID)
    if review.upload_type != expected_type:
        raise HttpError(400, f"This review is not of type {expected_type}")
    
    try:
        reviewer = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        raise HttpError(404, "Reviewer with provided email does not exist.")

    review.reviewer = reviewer
    review.submission_status = StatusChoices.STATUS_ASSIGNED.value
    review.save()

@router.get(
    "/ontology",
    summary = "API Query ontology reviews response submitter",
    description = "Query ontology reviews data structure",
    response = {200: list[schema.ListAllReviewsSchema]},
)
@PermissionChecker.has_permission(["ONTOLOGY_REVIEW"])
def get_ontology_reviews(request):
    results = Review.objects.filter(upload_type='UPLOAD_ONTOLOGY')
    return results


@router.get(
    "/ontology/{reviewID}",
    summary = "Detailed ontology review response with review ID", 
    description = "Get all the details for the ontology submitted using the review ID",
    response = {200: schema.ReviewDetailsOntologySchema},
)
@PermissionChecker.has_permission(["ONTOLOGY_REVIEW"])
def get_ontology_review_details(request, reviewID:int):
    try:
        review = Review.objects.get(id=reviewID)
        
        if review.upload_type != "UPLOAD_ONTOLOGY":
            raise HttpError(400, "This review is not of type UPLOAD_ONTOLOGY")
        
        return 200, review
    except Review.DoesNotExist:
        raise HttpError(404, "Review not found")
    
@router.post(
    "/ontology/{reviewID}/assign-to-review",
    summary="Assign ontology type review to a reviewer",
    description="Assigns a ontology type review to a reviewer based on their email",
    response={204: None},
)
@PermissionChecker.has_permission(["ONTOLOGY_REVIEW"])
def assign_ontology_review(
    request,
    reviewID: int,
    payload: schema.AssignReviewSchema = Body(...)
):
    review = get_object_or_404(Review, id=reviewID)
    
    if review.upload_type != "UPLOAD_ONTOLOGY":
        raise HttpError(400, f"This review is not of type UPLOAD_ONTOLOGY")
    
    try:
        reviewer = CustomUser.objects.get(email=payload.email)
    except CustomUser.DoesNotExist:
        raise HttpError(404, "Reviewer with provided email does not exist.")

    review.reviewer = reviewer
    review.submission_status = StatusChoices.STATUS_ASSIGNED.value
    review.save()
    
    return 204, None

@router.patch(
    "/ontology/{reviewID}",
    summary="Update review details for ontology type",
    description="Updates the submission status and review ontology details for a review",
    response={204: None},
)
@PermissionChecker.has_permission(["ONTOLOGY_REVIEW"])
def update_ontology_review(request, reviewID: int, payload: schema.ReviewUpdateSchema):
    review = get_object_or_404(Review, id=reviewID)
    
    if review.submission_status != "ASSIGNED":
        raise HttpError(403, "Review cant be edited")
    
    review_details, created = ReviewDetails.objects.get_or_create(reviewer_details_id=reviewID)

    review_details.status = payload.review.status
    review_details.comment = payload.review.comment
    review_details.save()
        
    review.submission_status = payload.submission_status
    review.save()

    if payload.submission_status == 'ACCEPTED' and not review.study:
        # Imports completely new ontology.
        logger.info(f"Loading new ontology after user '{request.user.email}' approved it.")
        import_rdf(review_details.modified_ontology)
        load_all_knowledge_node_classes(force_reload=True)
    elif payload.submission_status == 'ACCEPTED' and review.study:
        # Adds data from uploaded study to graph data base. 
        # Don't delete the review and study data from the db because it will still be needed by the feedback routes
        load_all_knowledge_node_classes(force_reload = True)
        review_details.modified_ontology = entities_to_rdf(get_codebooks_for_rdf(review.study))
        review_details.save()

        for migration in load_migrations(review.study):
            migration.apply()

        load_all_knowledge_node_classes(force_reload=True)

        # NOTE: Assuption: Neccesary changes to the ontology have been made and the assigned_meta_tag is added to the CodeBookColumn models
        graph_functions.build_study_codebook_knowledge_graph(review.study)

    return 204, None


@router.get(
    "/data",
    summary = "API Query data reviews list response submitter",
    description = "Query data reviews data structure",
    response = {200: list[schema.ListAllReviewsSchema]},
)
@PermissionChecker.has_permission(["DATA_REVIEW"])
def get_data_reviews(request):
    return Review.objects.filter(upload_type='UPLOAD_DATA')

@router.get(
    "/data/{reviewID}",
    summary = "Detailed data review response with review ID", 
    description = "Get all the details for the data type submitted using the review ID",
    response = {200: schema.ReviewDetailsDataSchema},
)
@PermissionChecker.has_permission(["DATA_REVIEW"])
def get_data_review_details(request, reviewID: int):
    try:
        review = get_object_or_404(Review, id=reviewID) # Fetch the Review object
        if review.upload_type != "UPLOAD_DATA":
            raise HttpError(400, "This review is not of type UPLOAD_DATA")
        return review 
    except Review.DoesNotExist:
        raise HttpError(404, "Review not found")

@router.post(
    "/data/{reviewID}/assign-to-review",
    summary="Assign data type review to a reviewer",
    description="Assigns a data type review to a reviewer based on their email",
    response={204: None, 400: str, 401: str, 403: str},
)
@PermissionChecker.has_permission(["DATA_REVIEW"])
def assign_data_review(
    request,
    reviewID: int,
    payload: schema.AssignReviewSchema = Body(...)
):
    assign_reviewer_logic(reviewID, payload.email, "UPLOAD_DATA")
    return 204, None
    
@router.patch(
    "/data/{reviewID}", 
    summary="Update review details for data type",
    description="Updates the submission status and review details for a data review",
    response={204: None, 400: str, 401: str, 403: str},
)
@PermissionChecker.has_permission(["DATA_REVIEW"])
def update_data_review(request, reviewID: int, payload: schema.ReviewUpdateSchema = Body(...)):
    review = get_object_or_404(Review, id=reviewID)
    
    if review.submission_status != "ASSIGNED":
        raise HttpError(403, "Review cant be edited")
    
    review_details, created = ReviewDetails.objects.get_or_create(reviewer_details_id=reviewID)

    review_details.status = payload.review.status
    review_details.comment = payload.review.comment
    review_details.save()
        
    review.submission_status = payload.submission_status
    review.save()

    if payload.submission_status == 'ACCEPTED' and review.study:
        #TODO: set graph is_verified = true + data node connection -> current_data
        # change the connection between leaf nodes and data nodes to current
        graph_functions.set_in_review_data_to_current_for_subgraph(graph_id = review.study.id)
        
        # set is_verified = true for all KnowledgeNodes and edges between KnowledgeNodes with graph_id = review.study.id
        graph_functions.set_is_verified_for_subgraph(graph_id = review.study.id, is_verified=True)
        
    elif (payload.submission_status == 'DECLINED' or payload.submission_status == 'MODIFICATION_NEEDED') and review.study:
        #TODO: Discuss if delete would be needed here
        pass
    return 204, None

@router.get(
   "/feedback",
    summary = "Query feedback data structure",
    description = "Query list of all the feedback data structures from both upload type ontology and data",
    response = {200: list[schema.FeedbackSimpleSchema]}, 
)
def get_list_feedback(request):
    ontology_feedbacks = Feedback.objects.filter(review__upload_type = UploadTypeChoices.UPLOAD_ONTOLOGY.value)
    data_feedbacks = Feedback.objects.filter(review__upload_type = UploadTypeChoices.UPLOAD_DATA.value)

    ontology_feedbacks = ontology_feedbacks.filter(review__submitter = request.user)
    data_feedbacks = data_feedbacks.filter(review__submitter = request.user)

    return list(ontology_feedbacks) + list(data_feedbacks)


@router.get(
    "/feedback/{feedbackID}",
    summary = "Query specific feedback for ontology and data upload submission", 
    description = "Get all the details for the data type or ontology type feedback submitted using the feedback ID",
    response = {200: schema.FeedbackDetailsSchema},
)
def get_feedback_details(request, feedbackID: int):
    return get_object_or_404(Feedback, id = feedbackID)
