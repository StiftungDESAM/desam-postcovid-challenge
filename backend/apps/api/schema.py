from reviewer.helper import get_data_rows_for_codebook
from pydantic import Field
import ninja 
from ninja import Schema
from django.utils import timezone
from datetime import date, datetime
from typing import Optional, List, Literal, Union, Any, Dict

from ontology.models import OntologyNode, OntologyRelationship, OntologyNodeTypes
from graph_migrations.studies import load_migrations, get_migration_steps
from study.models import Purpose, CodeBook
from study.helper import get_assigned_meta_field, get_code_books_for_study, get_column_idx_by_item, get_column_item_by_item, get_column_name_by_item, get_columns_for_code_book, get_data_quality_check_config_for_code_book, get_data_quality_check_config_values, get_id_of_code_book, get_linked_item_by_item, get_meta_for_code_book, get_name_of_code_book, get_row_cells_by_answer_group, get_row_idx_by_answer_group, get_rows, get_rows_for_code_book, get_study_from_knowledge_graph, get_tag_of_meta_field

from ontology.data_requests import get_codebooks_for_rdf
from ontology.diff import from_rdf, entities_to_rdf
from ontology import export

import logging
logger = logging.getLogger(__name__)

class NodeCount(ninja.Schema):
    count: int


class SimpleOntologyNodeSchema(ninja.Schema):
    tag: str
    name: str
    node_type: str = ninja.Field(..., alias="get_node_type_display")
    created_at: timezone.datetime


class UserData(ninja.Schema):
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    gender: str


class AccessDataCreation(ninja.Schema):
    role: List[str]
    permissions_requested: List[str]
    

class AccessData(ninja.Schema):
    role: List[str]
    permissions_requested: List[str]
    permissions_granted: List[str]
    
    @staticmethod
    def resolve_role(obj):
        return obj.role.values_list("name", flat=True)
    
    @staticmethod
    def resolve_permissions_requested(obj):
        return obj.permissions_requested.values_list("name", flat=True)
    
    @staticmethod
    def resolve_permissions_granted(obj):
        return obj.permissions_granted.values_list("name", flat=True)


class CredentialsData(ninja.Schema):
    email: str
    password: str
    
class UserRegistrationSchema(ninja.Schema):
    user: UserData
    access: AccessDataCreation
    credentials: CredentialsData


class CredentialsTokenSchema(ninja.Schema):
    email: str
    token: str

    @staticmethod
    def resolve_token(obj):
        return obj.token_set.get().key


class UserLoginSchema(ninja.Schema):
    user: UserData
    access: AccessData
    credentials: CredentialsTokenSchema

    @staticmethod
    def resolve_user(obj):
        return obj
    
    @staticmethod
    def resolve_access(obj):
        return obj
    
    @staticmethod
    def resolve_credentials(obj):
        return obj

class PermissionsVerificationSchema(ninja.Schema):
    permissions: List[str]

class Message(ninja.Schema):
    message: str


class OntologyMigrationSchema(ninja.Schema):
    # Old complicated type definition: Literal["LINKING", "UNLINKING", "RELINKING", "ATTRIBUTE_MODIFICATION", "CREATION", "ADDITION", "INSERTION_SINGLE", "INSERTION_MULTIPLE", "EXTENSION", "DELETION", "DELETION_PARTIAL", "DELETION_FULL", "DELETION_LEAF"]
    # Has been discarded because a dynamic ID is added to the main/sub attribute.
    main: str = ninja.Field(None, alias = "migration.full_name")
    sub: str | None = ninja.Field(None, alias = "name")

class OntologyMigrationStepSchema(ninja.Schema):
    id: int = None
    operation: OntologyMigrationSchema
    element_type: Literal['STAKEHOLDER', 'NODE', 'LEAF', 'RELATIONSHIP']
    name: str = ninja.Field(None, alias = "target.name")
    tag: str = ninja.Field(None, alias = "target.tag")

    @staticmethod
    def resolve_operation(obj):
        return obj

    @staticmethod
    def resolve_element_type(obj):
        if not isinstance(obj.target, (OntologyNode, OntologyRelationship)):
            raise ValueError("Invalid migration type: Only OntologyRelationship and OntologyNode are supported.")
        if isinstance(obj.target, OntologyRelationship):
            return "RELATIONSHIP"
        
        match obj.target.node_type:
            case OntologyNodeTypes.STAKEHOLDER:
                return "STAKEHOLDER"
            case OntologyNodeTypes.LEAF:
                return "LEAF"
            case _:
                return "NODE"

    
class CredentialsDataQuery(ninja.Schema):
    email: str
    
class UserQuerySchema(ninja.Schema):
    user: UserData = None
    access: AccessData = None
    credentials: CredentialsDataQuery = None
    
    account_verification: str 
    permission_verification: str
    
    @staticmethod
    def resolve_user(obj):
        return obj
    
    @staticmethod
    def resolve_access(obj):
        return obj
    
    @staticmethod
    def resolve_credentials(obj):
        return obj
    
    # TODO: Implement logic for "CODE EXPIRED" response
    @staticmethod
    def resolve_account_verification(self):
        return "VERIFIED" if self.email_verified else "NOT_VERIFIED"
    
    @staticmethod
    def resolve_permission_verification(self):
        return "VERIFIED" if self.permissions_verified else "NOT_VERIFIED"
    


class RDFSchema(ninja.Schema):
    rdf: str
    
class AdminUpdateAccessData(ninja.Schema):
    role: List[str]
    permissions_requested: List[str]
    permissions_granted: List[str]

class AdminUserUpdateSchema(ninja.Schema):
    user: UserData
    access: AdminUpdateAccessData
    account_verification: str 
    permission_verification: str
    
class RequestPasswordResetSchema(ninja.Schema):
    email: str
    
class PasswordResetSchema(ninja.Schema):
    code: str
    password: str
    

class SubmitterSchema(ninja.Schema):
    first_name:str
    last_name:str
    role:List[str]

    @staticmethod 
    def resolve_role(obj):
        return obj.role.values_list("name", flat=True)

class ReviewerSchema(ninja.Schema):
    first_name:str
    last_name:str
    email: str

class ListAllReviewsSchema(ninja.Schema):
    id:int
    submitter:SubmitterSchema 
    submission_date: timezone.datetime
    reviewer:  Optional[ReviewerSchema] = None
    submission_status: str

class ReviewStatusSchema(ninja.Schema):
    status: Optional[str] = ninja.Field(None, alias = "status")
    comment: Optional[str] = ninja.Field(None, alias = "comment")

class ReviewUpdateSchema(ninja.Schema):
    submission_status: Optional[str] = None
    review: Optional[ReviewStatusSchema] = None

class StudyInfoSchema(ninja.Schema):
    name: str
    purpose: Purpose
    description: Optional[str] = ""
    date_start: date
    date_end: date
    drks_id: str

class SubmissionDetailsOntologySchema(ninja.Schema):
    study_info: StudyInfoSchema | None
    modified_ontology: Optional[str] = ""
    migration_operations: List[OntologyMigrationStepSchema]

    @staticmethod
    def resolve_study_info(obj):
        return obj.study
    
    @staticmethod
    def resolve_migration_operations(obj):
        if not obj.study:
            return []
        migrations = load_migrations(obj.study)
        return get_migration_steps(migrations)
    
    @staticmethod
    def resolve_modified_ontology(obj):
        ontology = obj.details.modified_ontology
        #check ob es ein aufruf von mainteiner einreichung ist oder studie
        #bei studie
        if obj.study and obj.submission_status != "ACCEPTED":
            return entities_to_rdf(get_codebooks_for_rdf(obj.study))
        elif obj.study and obj.submission_status == "ACCEPTED":
            return obj.details.modified_ontology
        else:
            return from_rdf(obj.details.modified_ontology)


class ReviewDetailsOntologySchema(ninja.Schema):
    id:int
    submitter:SubmitterSchema 
    submission_date:timezone.datetime
    reviewer:Optional[ReviewerSchema] = None
    submission_status:str
    submission_details: Optional[SubmissionDetailsOntologySchema] = None
    review:ReviewStatusSchema

    @staticmethod
    def resolve_reviewer(obj):
        return obj.reviewer

    @staticmethod
    def resolve_submitter(obj):
        return obj.submitter
    
    @staticmethod
    def resolve_review(obj):
        return obj.details

    @staticmethod
    def resolve_submission_date(obj):
        return obj.submission_date

    @staticmethod
    def resolve_submission_status(obj):
        return obj.submission_status
    
    @staticmethod
    def resolve_submission_details(obj):
        return obj

class AssignReviewSchema(ninja.Schema):
    email: str    
  
class SystemStats(ninja.Schema):
    type: Literal['AMOUNT_STUDIES', 'AMOUNT_DATAPOINTS', 'AMOUNT_PARTICIPANTS', 'AMOUNT_USERS']
    amount: int

class SubmissionCodeBookSchema(Schema): # New schema for submission details
    id: int
    name: str
    data: List[List[str]]
    
    @staticmethod
    def resolve_id(obj):
        return obj.id 
    
    @staticmethod
    def resolve_name(obj):
        return obj.name 
    
    @staticmethod
    def resolve_data(obj):
        return get_data_rows_for_codebook(obj)
    
class SubmissionDetailsDataSchema(ninja.Schema):
    study_info: StudyInfoSchema
    data_ontology: Optional[str] = ""
    code_books: List[SubmissionCodeBookSchema]
    
    @staticmethod
    def resolve_study_info(obj):
        return obj.study
    
    @staticmethod
    def resolve_submitter(obj):
        return obj   
    
    @staticmethod
    def resolve_code_books(obj):
        return obj.study.codebooks  


class CodebookMappingRowSchema(ninja.Schema):
    row_id: int
    cells: List[Any]


class CodebookMetaAssignmentsSchema(ninja.Schema):
    header: str
    meta_data_item_tag: Optional[str] = None  # null/Number


class CodebookMappingSchema(ninja.Schema):
    columns: List[str]
    rows: List[CodebookMappingRowSchema]
    meta_assignments: List[CodebookMetaAssignmentsSchema]


class ColumnSchema(ninja.Schema):
    header: str
    assigned_meta_tag: Optional[str] = None  # null/String

class RowSchema(ninja.Schema):
    cells: List[str]
    row_id: int
    assigned_item_id: Optional[str] = None  # null/Number


class CodeBookSchema(ninja.Schema):
    name: str
    columns: List[ColumnSchema]
    rows: List[RowSchema]


class StudySubmissionSchema(ninja.Schema):
    study_info: StudyInfoSchema
    codebooks: List[CodeBookSchema]


class StudyResponseSchema(ninja.Schema):
    id: int
    name: str
    purpose: str
    description: str
    dateStart: Optional[date] = None
    dateEnd: Optional[date] = None
    drksID: str
    submitter: SubmitterSchema
    submissionDate: datetime
    amountCodeBooks: int


class CodebookResponseSchema(ninja.Schema):
    id: int
    name: str
    study: int
    uploader: int
    upload_date: str
    upload_timestamp: str
    field_names: Optional[List[str]] = None
    section_headings: Optional[List[str]] = None
    field_types: Optional[List[str]] = None
    questions: Optional[List[str]] = None
    mappings: Optional[List[str]] = None
    required_fields: Optional[List[bool]] = None
    mapping_column: Optional[str] = None
    translation_column: Optional[str] = None
    identifier_column: Optional[str] = None
    codebook_df: Optional[dict] = None
    mapping_candidates_knowledge_graph: Optional[List[List[Union[None, int]]]] = None
    mapping_candidates_knowledge_graph_similarity: Optional[List[List[Union[None, float]]]] = None
    assignedItemIDs: Optional[List[int]] = None
    assignedMetaFields: Optional[List[Union[dict, None]]] = None


class StudyUpdateSchema(ninja.Schema):
    name: Optional[str]
    purpose: Optional[str]
    description: Optional[str]
    dateStart: Optional[str]
    dateEnd: Optional[str]
    drksID: Optional[str]


class CodebookUpdateSchema(ninja.Schema):
    codebook_id: int  # The ID of the codebook to update
    name: Optional[str] = None
    field_names: Optional[List[str]] = None
    section_headings: Optional[List[str]] = None
    field_types: Optional[List[str]] = None
    questions: Optional[List[str]] = None
    mappings: Optional[List[str]] = None
    required_fields: Optional[List[bool]] = None
    mapping_column: Optional[str] = None
    translation_column: Optional[str] = None
    identifier_column: Optional[str] = None
    codebook_df: Optional[CodeBookSchema] = None
    mapping_candidates_knowledge_graph: Optional[List[Any]] = None
    mapping_candidates_knowledge_graph_similarity: Optional[List[Any]] = None
    assignedItemIDs: Optional[Any] = None
    assignedMetaFields: Optional[Any] = None
    
class ReviewDetailsDataSchema(ninja.Schema):
    id:int
    submitter:SubmitterSchema
    submission_date:timezone.datetime
    reviewer:Optional[ReviewerSchema] = None
    submission_status:str
    submission_details:SubmissionDetailsDataSchema
    review:ReviewStatusSchema

    @staticmethod
    def resolve_submitter(obj):
        return obj.submitter   

    @staticmethod
    def resolve_submission_date(obj):
        return obj.submission_date

    @staticmethod
    def resolve_reviewer(obj):
        return obj.reviewer

    @staticmethod
    def resolve_submission_status(obj):
        return obj.submission_status

    @staticmethod
    def resolve_review(obj):
        return obj.details
    
    @staticmethod
    def resolve_submission_details(obj):
        return obj

class OntologyNodeSchema(ninja.Schema):
    id: str = ninja.Field(None, alias = "uuid")
    tag: str
    name: str
    is_stakeholder: bool
    is_leaf: bool
    created: datetime = ninja.Field(None, alias = "created_at")
    last_updated: datetime = ninja.Field(None, alias = "updated_at")

    @staticmethod
    def resolve_is_stakeholder(obj):
        return obj.node_type == OntologyNodeTypes.STAKEHOLDER
    
    @staticmethod
    def resolve_is_leaf(obj):
        return obj.node_type == OntologyNodeTypes.LEAF
    
class MappedCodebookRow(ninja.Schema):
    row_id: int
    assigned_items: List[Dict[str, Any]]
    
    
class StudySchema(ninja.Schema):
    id: int
    study_info: StudyInfoSchema
    submitter: SubmitterSchema
    submission_date: timezone.datetime
    amount_questionnaires: int
    amount_data: int
    
    @staticmethod
    def resolve_amount_questionnaires(obj):
        return obj.codebooks.count()
    
    @staticmethod
    def resolve_amount_data(obj):
        amount_data = 0
        ontology_study = OntologyNode.nodes.first_or_none(tag="Studie")
        knowledge_studies = ontology_study.node_class.nodes.all()
        
        found_study = None
        
        for study in knowledge_studies:
            try:
                study_info = study.hat_studieninformationen.get_or_none(tag="Studieninformationen")
                
                study_id_node = study_info.hat_studienid.get_or_none(tag="StudienID")
                if study_id_node is None:
                    continue  # Skip if there's no StudienID

                study_id = study_id_node.current_data.get().value

                if str(study_id) == str(obj.id):
                    found_study = study
                    break
            except:
                logger.exception(f"Error processing study with node UUI {study.uuid}")
                continue
        
        if found_study is not None: 
            participants = found_study.hat_teilnehmer.filter(tag="Teilnehmer")
            
            for participant in participants:
                answer_groups = participant.gibt_antwortgruppe.filter(tag="Antwortgruppe")
                
                for group in answer_groups:
                    amount_data += len(group.hat_antwort.filter(tag="Antwort"))
        
        return amount_data
    
    @staticmethod
    def resolve_study_info(obj):
        return obj

class DataQualityCheckConfig(ninja.Schema):
    VALUE_TYPE: Optional[str] = Field(alias="value_type")
    VALUE_RANGE_MIN: Optional[str] = Field(alias="value_range_min")
    VALUE_RANGE_MAX: Optional[str] = Field(alias="value_range_max")
    VALUE_MAPPING: Optional[str] = Field(alias="value_mapping")
    VALUE_REQUIRED: Optional[str] = Field(alias="value_required")
    EMPTY_VALUES: bool = Field(alias="empty_values")
    EMPTY_ROWS: bool = Field(alias="empty_rows")
    EMPTY_COLUMNS: bool = Field(alias="empty_columns")
    mappingSeparator: Optional[str] = Field(alias="mapping_separator")
    answerSeparator: Optional[str] = Field(alias="answer_separator")

    class Config:
        populate_by_name = True
        populate_by_alias = True
        alias_generator = None
        
class CodeBookMeta(ninja.Schema):
    idx: int
    tag: str
    header: str
    rows: List[str]
    assigned_meta_field: Optional[OntologyNodeSchema] = None

    @staticmethod
    def resolve_tag(obj):
        return get_tag_of_meta_field(obj)

    @staticmethod
    def resolve_assigned_meta_field(obj):
        return get_assigned_meta_field(obj)
    
    @staticmethod
    def resolve_rows(obj):
        return get_rows(obj)
    
class CodeBookColumn(ninja.Schema):
    idx: int
    column_name: str
    item: Dict[str, Union[str, float, int, bool]]
    linked_item: Optional[Dict[str, Union[str, float, int, bool]]] = None
    
    @staticmethod
    def resolve_idx(obj):
        return get_column_idx_by_item(obj)
    
    @staticmethod
    def resolve_item(obj):
        return get_column_item_by_item(obj)
    
    @staticmethod
    def resolve_column_name(obj):
        return get_column_name_by_item(obj)
    
    @staticmethod
    def resolve_linked_item(obj):
        return get_linked_item_by_item(obj)
    
class CodeBookRow(ninja.Schema):
    idx: int
    cells: List[str]
    
    @staticmethod
    def resolve_idx(obj):
        return get_row_idx_by_answer_group(obj)
    
    @staticmethod
    def resolve_cells(obj):
        return get_row_cells_by_answer_group(obj)

class CodeBook(ninja.Schema):
    id: int
    name: str
    data_quality_check_config: Optional[DataQualityCheckConfig] = None
    mapping_column: Optional[str] = "Feldname"
    translation_column: Optional[str] = ""
    meta: List[CodeBookMeta]
    columns: List[CodeBookColumn]
    rows: List[CodeBookRow]
    
    @staticmethod
    def resolve_id(obj):
        return get_id_of_code_book(obj)
    
    @staticmethod
    def resolve_name(obj):
        return get_name_of_code_book(obj)
    
    @staticmethod
    def resolve_data_quality_check_config(obj):
        dqcc = get_data_quality_check_config_for_code_book(obj)
        if dqcc is not None:
            config_data = get_data_quality_check_config_values(dqcc) 
            return DataQualityCheckConfig.model_validate(config_data, from_attributes=True)
        else:
            return None

    @staticmethod
    def resolve_meta(obj):
        return get_meta_for_code_book(obj, get_id_of_code_book(obj))
    
    @staticmethod
    def resolve_columns(obj):
        columns = get_columns_for_code_book(obj)
        
        for column in columns:
            column._study_id = obj._study_id
            column._codebook_id = get_id_of_code_book(obj)

        return columns
    
    @staticmethod
    def resolve_rows(obj):
        rows = get_rows_for_code_book(obj)
        
        for row in rows:
            row._study_id = obj._study_id
            row._codebook_id = get_id_of_code_book(obj)

        return rows
    
class DetailedStudySchema(ninja.Schema):
    id: int
    study_info: StudyInfoSchema
    submitter: SubmitterSchema
    submission_date: timezone.datetime
    code_books: List[CodeBook]
    
    @staticmethod
    def resolve_study_info(obj):
        return obj
    
    @staticmethod
    def resolve_code_books(obj):
        code_books, study_id = get_code_books_for_study(*get_study_from_knowledge_graph(obj.id))
        for cb in code_books:
            cb._study_id = study_id
            
        return code_books
    
class StudyDataSubmissionSchema(ninja.Schema):
    code_book_id: int
    data_quality_check_config: DataQualityCheckConfig
    values: List[List[str]]


class CodeBookDataDataSchema(Schema):
    id: int
    name: str
    data: List[List[Optional[str]]]  

class CodeBookDataOntologyColumnSchema(Schema):
    id: int
    name: str
    rows: List[Optional[str]]
class CodeBookDataOntologySchema(Schema):
    id: int
    name: str
    data: List[CodeBookDataOntologyColumnSchema]    

class FeedbackSubmissionDetailsSchema(ninja.Schema):
    study_info: Optional[StudyInfoSchema] = ninja.Field(None, alias = "study")
    upload_type: str
    code_books: List[Union[CodeBookDataDataSchema, CodeBookDataOntologySchema]]

    @staticmethod
    def resolve_code_books(obj):
        codebooks_data = []
        if obj.study:
            codebooks = obj.study.codebooks.prefetch_related('rows', 'columns')
            for codebook in codebooks:
                codebook_info = {"id": codebook.id, "name": codebook.name}
                if obj.upload_type == "UPLOAD_DATA":
                    rows_data = get_data_rows_for_codebook(codebook)
                    codebooks_data.append(CodeBookDataDataSchema(**codebook_info, data=rows_data))
                elif obj.upload_type == "UPLOAD_ONTOLOGY":
                    ontology_data = []
                    columns_list = list(codebook.columns.all())
                    rows_list = list(codebook.rows.all())
                    if columns_list:
                        for i, column in enumerate(columns_list):
                            column_values = [rows_list[j].cells[i] if 0 <= i < len(rows_list[j].cells) else None for j in range(len(rows_list))]
                            ontology_data.append(CodeBookDataOntologyColumnSchema(id=i + 1, name=column.header, rows=column_values))
                    codebooks_data.append(CodeBookDataOntologySchema(**codebook_info, data=ontology_data))
        return codebooks_data

class FeedbackSimpleSchema(ninja.Schema):
    id: int

    name: Optional[str] = ninja.Field(None, alias = "review.study.name")
    purpose: Optional[str] = ninja.Field(None, alias = "review.study.purpose")
    date_start: Optional[date] = ninja.Field(None, alias = "review.study.date_start")
    date_end: Optional[date] = ninja.Field(None, alias = "review.study.date_end")
    submission_date: timezone.datetime = ninja.Field(None, alias = "review.submission_date")
    amount_code_books: int = ninja.Field(default = 0)
    upload_type: str = ninja.Field(None, alias = "review.upload_type")
    reviewer: Optional[ReviewerSchema] = ninja.Field(None, alias = "review.reviewer")
    submission_status: str = ninja.Field(None, alias = "review.submission_status")
    
    @staticmethod
    def resolve_amount_code_books(obj):
        if obj.review.study:
            return obj.review.study.codebooks.count()
        return 0
        
class FeedbackDetailsSchema(ninja.Schema):
    id: int
    submission_date: timezone.datetime = ninja.Field(None, alias = "review.submission_date")
    reviewer: Optional[ReviewerSchema] = ninja.Field(None, alias = "review.reviewer")
    submission_status: str = ninja.Field(None, alias = "review.submission_status")
    submission_details: FeedbackSubmissionDetailsSchema
    review: ReviewStatusSchema
    
    @staticmethod
    def resolve_submission_details(obj):
        return obj.review
    
    @staticmethod
    def resolve_review(obj):
        return obj.review.details
        # if hasattr(obj.review, 'details') and obj.review.details:
        #     return {
        #         "status": getattr(obj.review.details, 'status', None),
        #         "comment": getattr(obj.review.details, 'comment', None)
        #     }
        # return {"status": None, "comment": None}
        # return obj.review.details
    

class ItemSchema(ninja.Schema):
    id: str = ninja.Field(None, alias = "uuid")
    amount_answers: int
    item_meta: dict

    @staticmethod
    def resolve_amount_answers(obj):
        # NOTE: It might be good to annotate the answer counts in bulk instead of using individual queries.
        return export.get_answer_count(obj)
    
    @staticmethod
    def resolve_item_meta(obj):
        meta_fields = export.get_meta_nodes_for_item(obj)
     
        return {
            meta_field.tag: dict(
                tag=meta_field.tag,
                name= OntologyNode.nodes.first_or_none(tag=meta_field.tag).name,
                value= meta_field.current_data.get().value
            ) for meta_field in meta_fields
        }

class CSVExportSchema(ninja.Schema):
    csv: str

class JSONExportSchema(ninja.Schema):
    data : Dict[str, List[Union[str, float, int, bool]]]

    
class HighlightedStudy(ninja.Schema):
    id: int
    name: str
    questionnaires: int = 0
    questions: int = 0
    participants: int = 0
    datapoints: int = 0

