from api.transactions import TransactionRouter

from django.shortcuts import get_object_or_404
from django.utils import timezone
from neomodel import db
from ninja.errors import HttpError

from api import schema
from api.permissions import PermissionChecker
from graph_migrations.operations import GraphMigrationError
from graph_migrations.studies import save_migrations
from knowledge.graph_functions import add_study_data_to_knowledge_graph
from ontology.data_requests import get_codebooks_for_rdf
from ontology.diff import entities_to_rdf
from ontology.utils import get_all_outgoing_relationships
from ontology.models import OntologyNode
from reviewer.models import Review, ReviewDetails, StatusChoices, UploadTypeChoices, Feedback
from study.helper import get_study_from_knowledge_graph
from study.models import CodeBook, CodeBookColumn, CodeBookRow, Study
from study.utils import calculate_string_distance

import math
from typing import List
import logging
logger = logging.getLogger(__name__)

router = TransactionRouter()
LEVENSHTEIN_THRESHOLD = 0.6

@router.post(
    "/mapping",
    summary="Maps a codebook to our knowledge graph (Note: not finished (!))",
    description="This endpoint is used to map the provided codebook to our knowledge graph. (Note: not finished (!))",
    response={200: List[schema.MappedCodebookRow]},
)
@PermissionChecker.has_permission(["ONTOLOGY_UPLOAD"])
def map_codebook(request, codebook_mapping_schema: schema.CodebookMappingSchema):
    mapped_rows = []
    mapped_columns = [col for col in codebook_mapping_schema.meta_assignments if col.meta_data_item_tag is not None]
    
    if not mapped_columns:
        return 200, mapped_rows

    similarity_threshold = math.ceil(len(mapped_columns) / 2)
    
    # Preload ontology and knowledge item metadata
    ontology_item = OntologyNode.nodes.first_or_none(tag="Item")
    knowledge_items = ontology_item.node_class.nodes.all()
    meta_data_dicts = extract_metadata_dicts(knowledge_items)

    column_header_to_index = {header: idx for idx, header in enumerate(codebook_mapping_schema.columns)}

    for row in codebook_mapping_schema.rows:
        row_data = {col.meta_data_item_tag: row.cells[column_header_to_index[col.header]] for col in mapped_columns}

        candidates = calculate_candidates(
            similarity_threshold,
            meta_data_dicts,
            row_data
        )

        mapped_rows.append({
            "row_id": row.row_id,
            "assigned_items": candidates
        })

    return 200, mapped_rows


def extract_metadata_dicts(knowledge_items):
    meta_data_dicts = []

    for item in knowledge_items:
        meta_data = {
            "id": item.uuid
            # "id": int(item.element_id_property.split(":")[-1])
        }
        
        item_meta = item.hat_metadaten.get_or_none(tag="Metadaten")
        
        if item_meta:
            for rel in get_all_outgoing_relationships(item_meta):
                meta_data[rel.end_node.tag] = rel.end_node.current_data.get().value
        
        meta_data_dicts.append(meta_data)

    return meta_data_dicts


def calculate_candidates(similarity_threshold, meta_data_dicts, input_values):
    candidates = []

    for meta_data in meta_data_dicts:
        match_count = sum(
            1
            for key, input_value in input_values.items()
            if (meta_value := meta_data.get(key)) 
            and input_value 
            and string_similarity(meta_value, input_value) >= LEVENSHTEIN_THRESHOLD
        )

        if match_count >= similarity_threshold:
            candidates.append(meta_data)

    return candidates


def string_similarity(s1, s2):
    distance = calculate_string_distance(s=s1, t=s2, algorithm='levenshtein')
    return 1 - (distance / max(len(s1), len(s2)))

@router.post(
    "/",
    summary="Submit a study",
    description="This endpoint is used to submit a study and the codebooks associated to it.purpose needs to"
                "be a valid purpose ['FEASIBILITY_CHECK', 'PILOT_STUDY', 'DATA_ANALYSIS', 'DATA_COLLECTION', "
                "'INTERVENTION_RESEARCH'], 'date_start' and 'date_end' need to be string encoded dates ('YYYY-MM-DD').",
    response={200: None}
)
@PermissionChecker.has_permission(["ONTOLOGY_UPLOAD"])
def submit_study(request, study: schema.StudySubmissionSchema):
    current_user = request.user
    
    # Save data from study in DB
    study_instance = Study.objects.create(
        submitter=current_user,
        name=study.study_info.name,
        purpose=study.study_info.purpose,
        description=study.study_info.description,
        date_start=study.study_info.date_start,
        date_end=study.study_info.date_end,
        drks_id=study.study_info.drks_id
    )
    
    # Save the CodeBooks
    for codebook_data in study.codebooks:
        codebook_instance = CodeBook.objects.create(
            study=study_instance,
            name=codebook_data.name,
        )
        
        # Save the rows in each CodeBook
        for idx, column_data in enumerate(codebook_data.columns):
            CodeBookColumn.objects.create(
                codebook=codebook_instance,
                idx=idx,
                header=column_data.header,
                assigned_meta_tag=column_data.assigned_meta_tag
            )
        
        # Save the rows in each CodeBook
        for row_data in codebook_data.rows:
            CodeBookRow.objects.create(
                codebook=codebook_instance,
                row_id=row_data.row_id,
                cells=row_data.cells,
                assigned_item_id=row_data.assigned_item_id
            )
    
    # Create new review process in DB
    review_instance = Review.objects.create(
        submitter=current_user,
        submission_date=timezone.now(),
        study=study_instance,
        submission_status=StatusChoices.STATUS_OPEN.value,
        upload_type=UploadTypeChoices.UPLOAD_ONTOLOGY.value 
    )
    modified_ontology = ""
    #entities = get_codebooks_for_rdf(study_instance)
    #rdf = entities_to_rdf(entities)
    #logger.debug(rdf)
    reviewDetail =ReviewDetails.objects.create(
        reviewer_details=review_instance,
        status=None, 
        comment=None,
        modified_ontology=modified_ontology,
    )

    # Calculates the necessary graph database migrations and saves them.
    try:
        save_migrations(study_instance)
    except GraphMigrationError as exec:
        logger.debug(str(exec))
        raise HttpError(400,str(exec))
    entities = get_codebooks_for_rdf(study_instance)
    rdf = entities_to_rdf(entities)
    reviewDetail.modified_ontology=rdf
    reviewDetail.save()
    Feedback.objects.create(review=review_instance)

    return 200, None

@router.get(
    "/",
    summary="Gets all studies that are registered in the system",
    description="This endpoint gets all studies that are registered in the system",
    response={200: List[schema.StudySchema]},
)
@PermissionChecker.has_permission(["DATA_VIEW", "DATA_UPLOAD"], require_all=False)
def get_all_studies(request, for_route: str):
    all_studies = Study.objects.all()
    valid_studies = []
    for study in all_studies:
        filter_study = False
        all_reviews = study.reviews.all()
        for review in all_reviews:
            if for_route == 'UPLOAD':
                if (review.upload_type == "UPLOAD_ONTOLOGY" and review.submission_status != "ACCEPTED") or review.upload_type == "UPLOAD_DATA":
                    filter_study = True
                    break
            elif for_route == 'VIEW':
                if (review.upload_type == "UPLOAD_ONTOLOGY" and review.submission_status != "ACCEPTED") or (review.upload_type == "UPLOAD_DATA" and review.submission_status != "ACCEPTED"):
                    filter_study = True
                    break
        
        if for_route == 'VIEW' and len(all_reviews.filter(upload_type="UPLOAD_DATA",submission_status="ACCEPTED")) == 0:
            filter_study = True
        
        if not filter_study:
            valid_studies.append(study)
                
    return 200, valid_studies

@router.get(
    "/{id}",
    summary="Gets a detailed study by its id",
    description="This endpoint gets a detailed study by its id",
    response={200: schema.DetailedStudySchema},
)
@PermissionChecker.has_permission(["DATA_VIEW", "DATA_UPLOAD"], require_all=False)
def get_study_by_id(request, id: int):
    requested_study = get_object_or_404(Study, id=id)
    study, study_id = get_study_from_knowledge_graph(id)

    if study is not None:
        return 200, requested_study
    else:
        raise HttpError(404, f"Study with id {id} doesn't have any data yet")    
    
@router.post(
    "/{id}/data",
    summary="Adds data to a study",
    description="This endpoint adds data to a study",
    response={201: None},
)
@PermissionChecker.has_permission(["DATA_UPLOAD"])
def submit_data_to_study(request, id: int, data: list[schema.StudyDataSubmissionSchema]):
    study = get_object_or_404(Study, id=id)  
    
    studien_id_ontology_node = OntologyNode.nodes.first_or_none(tag="StudienID")
    
    if not studien_id_ontology_node:
        raise HttpError(404, "Ontology node 'StudienID' not found")

    StudienID = studien_id_ontology_node.node_class
    studien_id = StudienID.nodes.first_or_none(current_data__value = str(id))
    graph_id = studien_id[0].graph_id
    
    if not studien_id:
        raise HttpError(404, f"Knowledge node 'StudienID' with data node value {id} not found")
   
    #Check if study graph has data already
    answer_ontology_node = OntologyNode.nodes.first_or_none(tag="Antwort")
    Answer = answer_ontology_node.node_class
    
    if len(Answer.nodes.filter(graph_id=graph_id)) > 0:
        raise HttpError(403, f"Study already has associated data")
        
    # Check if data for all codebooks is uploaded
    questionnaire_id_ontology_node = OntologyNode.nodes.first_or_none(tag="FragebogenID")
    Questionnaire_id = questionnaire_id_ontology_node.node_class
    
    questionnaire_ids = Questionnaire_id.nodes.filter(graph_id=graph_id)
    
    if(len(questionnaire_ids) != len(data)):
        raise HttpError(400, f"Mismatch in amount of data uploaded and amount of questionnaires for this study")
        
    wanted_questionnaire_ids = [d.code_book_id for d in data]
    mapped_questionnaire_ids = [q.current_data.get().value for q in questionnaire_ids]
    for wanted_id in wanted_questionnaire_ids:
        if str(wanted_id) not in mapped_questionnaire_ids:
            raise HttpError(400, f"Questionnaire {wanted_id} not found for study {id}")
            
    # Add data to the graph
    add_study_data_to_knowledge_graph(study_id = id , data = data)
    
    # Add review and feedback
    review_instance = Review.objects.create(
        submitter=request.user,
        submission_date=timezone.now(),
        study=study,
        submission_status=StatusChoices.STATUS_OPEN.value,
        upload_type=UploadTypeChoices.UPLOAD_DATA.value 
    )
    
    ReviewDetails.objects.create(
        reviewer_details=review_instance,
        status=None, 
        comment=None,
        modified_ontology="",
    )
    
    Feedback.objects.create(review=review_instance)
    
    return 201, None
    # raise HttpError(500, f"WANTED ERROR")
