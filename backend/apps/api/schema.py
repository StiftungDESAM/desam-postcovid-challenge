import ninja

from django.utils import timezone
from datetime import date
from typing import Optional, List, Literal

from ontology.models import OntologyNode, OntologyRelationship, OntologyNodeTypes


class NodeCount(ninja.Schema):
    count: int


class OntologyNodeSchema(ninja.Schema):
    name: str
    tag: str
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
    main: Literal["LINKING", "UNLINKING", "RELINKING", "ATTRIBUTE_MODIFICATION", "CREATION", "ADDITION", "INSERTION_SINGLE", "INSERTION_MULTIPLE", "EXTENSION", "DELETION", "DELETION_PARTIAL", "DELETION_FULL", "DELETION_LEAF"] = ninja.Field(None, alias = "migration.title")
    sub: Literal["LINKING", "UNLINKING", "RELINKING", "ATTRIBUTE_MODIFICATION", "CREATION", "ADDITION", "INSERTION_SINGLE", "INSERTION_MULTIPLE", "EXTENSION", "DELETION", "DELETION_PARTIAL", "DELETION_FULL", "DELETION_LEAF"] | None = ninja.Field(None, alias = "title")

class OntologyMigrationStepSchema(ninja.Schema):
    # id: int # NOTE: Currently no IDs are generated for migrations or migration steps.
    operation: OntologyMigrationSchema
    element_type: Literal['STAKEHOLDER', 'NODE', 'LEAF', 'RELATIONSHIP']
    name: str = ninja.Field(None, alias = "target.name")
    tag: str = ninja.Field(None, alias = "target.tag")

    @staticmethod
    def resolve_operation(migration_step):
        return migration_step

    @staticmethod
    def resolve_element_type(migration_step):
        if not isinstance(migration_step.target, (OntologyNode, OntologyRelationship)):
            raise ValueError("Invalid migration type: Only OntologyRelationship and OntologyNode are supported.")

        if isinstance(migration_step.target, OntologyRelationship):
            return "RELATIONSHIP"
        
        match migration_step.target.node_type:
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
    

    
