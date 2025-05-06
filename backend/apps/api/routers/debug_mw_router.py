from api.transactions import TransactionRouter

from django.conf import settings
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from neomodel import db
from ninja.errors import HttpError

from api import schema
from authentication.models import CustomUser
from knowledge import graph_functions
from ontology.models import OntologyNode
from reviewer.models import Review
from study.models import CodeBook, Study

import logging
logger = logging.getLogger(__name__)

router = TransactionRouter()

    
@router.get(
    "/users",
    summary="Get all users",
    description="Retrieve a list of all registered users for admin panel",
    response={200: list[schema.UserQuerySchema]},
    auth=None,
)
def get_all_users_admin(request):
    """Fetch all users with their details, including roles and permissions."""
    
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    return 200, CustomUser.objects.all()          


@router.post(
    "/user/{email}/verify-user",
    summary="Verify user",
    description="Verify a user (verify email and activate user)",
    auth=None,
    response={200: None},
)
def verify_user(request, email: str):
    """Verify a user."""
    
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    email = email.lower().strip()
    
    user = get_object_or_404(CustomUser, email=email)
    user.is_active = True
    user.email_verified = True
    user.save()

    return 200, None


@router.post(
    "/user/{email}/verify-user-email",
    summary="Verify user email",
    description="Verify the email of a user ",
    auth=None,
    response={200: None},
)
def verify_user_email(request, email: str):
    """Verify a user."""
    
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    email = email.lower().strip()
    
    user = get_object_or_404(CustomUser, email=email)
    user.email_verified = True
    user.save()

    return 200, None


@router.post(
    "/user/{email}/activate-user",
    summary="activate user",
    description="activate a user (based on email) ",
    auth=None,
    response={200: None},
)
def activate_user(request, email: str):
    """Activate a user."""
    
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    email = email.lower().strip()
    
    user = get_object_or_404(CustomUser, email=email)
    user.is_active = True
    user.save()

    return 200, None


@router.post(
    "/user/{email}/deactivate-user",
    summary="deactivate user",
    description="deactivate a user (based on email) ",
    auth=None,
    response={200: None},
)
def deactivate_user(request, email: str):
    """Deactivate a user."""
    
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    email = email.lower().strip()
    
    user = get_object_or_404(CustomUser, email=email)
    user.is_active = False
    user.email_verified = False
    user.save()

    return 200, None


@router.get(
    "/debug/users_detailed",
    summary="Get all users",
    description="Retrieve a list of all registered users",
    auth=None,
    response={200: list[dict]}
)
def get_all_users_detailed(request):
    """Fetch all users with their details, including roles and permissions."""
    
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    users = CustomUser.objects.all()

    user_list = []
    for user in users:
        user_data = model_to_dict(user, exclude=["password"])  # Exclude sensitive data
        user_data["role"] = list(user.role.all().values_list("name", flat=True))
        user_data["permissions_requested"] = list(user.permissions_requested.all().values_list("name", flat=True))
        user_data["permissions_granted"] = list(user.permissions_granted.all().values_list("name", flat=True))
        user_list.append(user_data)

    return 200, user_list



@router.get(
    "/study_detailed",
    summary="Get all users",
    description="Retrieve a list of all registered users",
    auth=None,
    response={200: list[dict]}
)
def get_studies_detailed(request):
    """Fetch all studies their details."""
    
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    studies = Study.objects.all()

    study_list = []
    for study in studies:
        study_data = model_to_dict(study)  # Exclude sensitive data
        
        study_list.append(study_data)

    return 200, study_list



@router.get(
    "/codebooks_detailed",
    summary="Get all codebooks",
    description="Retrieve a list of all codebooks",
    auth=None,
    response={200: list[dict]}
)
def get_codebooks_detailed(request):
    """Fetch all studies their details."""
    
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    codebooks = CodeBook.objects.all()
    
    logger.debug(f"Codebooks: {codebooks}")
    
    
    codebook_list = []
    for codebook in codebooks:
        codebook_data = model_to_dict(codebook)  # Exclude sensitive data
        codebook_data["rows"] = model_to_dict(codebook.rows.all())
        codebook_list.append(codebook_data)
    

    return 200, codebook_list


@router.get(
    "/study-query-tests",
    summary="Test query for study and codebooks",
    description="Test query for study and codebooks",
    auth=None,
    response={200: list[dict]}
)
def get_study_codebook_test(request):
    """Fetch studies."""
    
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    studies = Study.objects.filter(drks_id="DRKS000Test01")
    
    logger.debug(f"Study: {studies}")
    
    study_list = []
    
    for study in studies:
        study_data = model_to_dict(study)
        study_list.append(study_data)
        logger.debug(f"Codebook: {study.codebooks.all()}")
    

    return 200, study_list

@router.get(
    "/ontology/{reviewID}",
    summary = "Detailed ontology review response with review ID", 
    description = "Get all the details for the ontology submitted using the review ID",
    response = {200: schema.ReviewDetailsOntologySchema}, 
    auth=None,
)
def get_ontology_review_details_test(request, reviewID:int):
    try:
        review = Review.objects.get(id=reviewID)
        
        logger.debug(f"Review: {review}")
        logger.debug(f"Review.study: {review.study}")
        logger.debug(f"Review.study.id: {review.study.id}")
        logger.debug(f"Review.study.drks_id: {review.study.drks_id}")
        
        logger.debug(f"Review.study.codebooks: {review.study.codebooks.all()}")
        
        logger.debug(f"Review.study.codebook_id: {review.study.codebooks.all()[0].id}")
        
        logger.debug(f"Review.study.codebooks.rows: {review.study.codebooks.all()[0].rows.all()}")
        logger.debug(f"Review.study.codebooks.rows[0]: {review.study.codebooks.all()[0].rows.all()[0]}")
        logger.debug(f"Review.study.codebooks.rows[0].cells: {review.study.codebooks.all()[0].rows.all()[0].cells}")
        logger.debug(f"Review.study.codebooks.rows[0].cells: {review.study.codebooks.all()[0].rows.all()[0].assigned_item_id}")        
        logger.debug(f"Review.study.codebooks.rows[0].cells: {review.study.codebooks.all()[0].rows.all()[2].cells}")
        logger.debug(f"Review.study.codebooks.rows[0].cells: {review.study.codebooks.all()[0].rows.all()[2].assigned_item_id}")
        
        for col in review.study.codebooks.all()[0].columns.all():
            logger.debug(f"Review.study.codebooks.rows: {col}")
            logger.debug(f"Review.study.codebooks.rows: {col.header}")
            logger.debug(f"Review.study.codebooks.rows: {col.assigned_meta_tag}")
            
        for row in review.study.codebooks.all()[0].rows.all():
            logger.debug(f"Review.study.codebooks.rows: {row}")
            logger.debug(f"Review.study.codebooks.rows: {row.cells}")
            logger.debug(f"Review.study.codebooks.rows: {row.assigned_item_id}")
        
        logger.debug(f"Review.study.codebooks.rows: {review.study.codebooks.all()[0].columns.all()}")
        
        logger.debug(f"Review.details: {review.details}")
        logger.debug(f"Review.details: {review.details}")
        
        
        if review.upload_type != "UPLOAD_ONTOLOGY":
            raise HttpError(400, "This review is not of type UPLOAD_ONTOLOGY")
        
        return 200, review
    except Review.DoesNotExist:
        raise HttpError(404, "Review not found")
    
    
    
@router.post(
    "/test-knowledge-creation/{study_internal_id}",
    summary = "Create knowledge nodes for a simple test study",
    response = {201: None}
)
def post_knowledge_test_from_study_model(request, study_internal_id: int):
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")
    
    review = Review.objects.get(id=study_internal_id)
    
    if review.study:
        graph_functions.build_study_codebook_knowledge_graph(review.study)
    
    
    return 201, None


@router.post(
    "/test-quality-check-creation",
    summary = "Create knowledge nodes for quality check",
    response = {201: None}
)
def post_quality_check_test(request, graph_id: int, codebook_id: int ,data_qualitycheck_config: schema.DataQualityCheckConfig):
    
    
    graph_functions.build_and_attach_quality_check_subgraph(graph_id = graph_id, codebook_id = codebook_id, data_qualitycheck_config = data_qualitycheck_config)
    
    return 201, None
    


@router.post(
    "/test-build-or-update-answer-group",
    summary = "builds a answer group, update not implemented",
    response = {201: None}
)
def post_answer_group_test(request, study_id: int, codebook_id: int, row_id: int, data_row: list[str], mapping_row: list[str]):
    
    studie_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="Studie")
    if not studie_ontology_node:
        raise HttpError(404, "Ontology node 'Studie' not found")
    
    Studie = studie_ontology_node.node_class
    
    current_study = Studie.nodes.first_or_none(hat_studieninformationen__hat_studienid__current_data__value = str(study_id))[0]
    
    # get graph id of the study 
    graph_id = current_study.graph_id
    data_graph_parameters_dict = {"graph_id": graph_id}
    
    current_patient_id = data_row[0]
    
    #participant_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Teilnehmer")
    #Participant = participant_node.node_class
    
    patient_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Patient")
    Patient = patient_node.node_class
    
    current_patient_current = Patient.nodes.first_or_none(hat_patientid__current_data__value = current_patient_id, graph_id = graph_id)
    current_patient_in_review = Patient.nodes.first_or_none(hat_patientid__in_review__value = current_patient_id, graph_id = graph_id)

    if current_patient_current:
        current_participant = current_patient_current[0].ist_teilnehmer.single()
        
    if current_patient_in_review:
        current_participant = current_patient_in_review[0].ist_teilnehmer.single()
    
    
    # TODO: assumption: all in review data of this study for the current study graph was deleted
    if not (current_patient_current or current_patient_in_review):
        current_participant = graph_functions.add_new_patient_to_study(patient_id = current_patient_id, graph_id = graph_id)        
        current_study.hat_teilnehmer.connect(current_participant, data_graph_parameters_dict)
    
    
    graph_functions.build_or_update_answer_group_from_data(current_participant = current_participant, 
                                                           mapping_row = mapping_row, 
                                                           row_id = row_id, 
                                                           data_row = data_row, 
                                                           graph_id = graph_id, 
                                                           codebook_id = codebook_id
)
    
    
    return 201, None
    
    
@router.post(
    "/test-add_study_data_to_knowledge_graph",
    summary = "Create knowledge nodes for StudyDataSubmission",
    response = {201: None}
)
def post_add_study_data_test(request, id: int, data: list[schema.StudyDataSubmissionSchema]):
    
    
    
    studien_id_ontology_node = OntologyNode.nodes.first_or_none(tag="StudienID")
    
    if not studien_id_ontology_node:
        raise HttpError(404, "Ontology node 'StudienID' not found")

    StudienID = studien_id_ontology_node.node_class
    
    if not StudienID.nodes.first_or_none(current_data__value = str(id)):
        raise HttpError(404, f"Knowledge node 'StudienID' with data node value {id} not found")
    
    graph_functions.add_study_data_to_knowledge_graph(study_id = id , data = data)
    
    return 201, None