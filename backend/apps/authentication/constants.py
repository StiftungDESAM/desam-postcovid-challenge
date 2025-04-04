
ROLE_CHOICES = [
    ("SUPER_ADMIN", "SUPER_ADMIN"),
    ("ADMIN", "ADMIN"),
    ("MAINTAINER", "MAINTAINER"),
    ("RESEARCHER", "RESEARCHER"),
    ("PRACTITIONER", "PRACTITIONER"),
]

SCOPE_CHOICES = [
    ("SUPER_ADMIN", "SUPER_ADMIN"),
    ("ADMIN", "ADMIN"),
    ("DATA_EXPORT", "DATA_EXPORT"),
    ("DATA_REVIEW", "DATA_REVIEW"),
    ("DATA_UPLOAD", "DATA_UPLOAD"),
    ("DATA_VIEW", "DATA_VIEW"),
    ("ONTOLOGY_EXPORT", "ONTOLOGY_EXPORT"),
    ("ONTOLOGY_REVIEW", "ONTOLOGY_REVIEW"),
    ("ONTOLOGY_UPLOAD", "ONTOLOGY_UPLOAD"),
    ("ONTOLOGY_VIEW", "ONTOLOGY_VIEW"),
    
]

# Helper functions to get just the names
def get_role_names():
    return [role[0] for role in ROLE_CHOICES]

def get_scope_names():
    return [scope[0] for scope in SCOPE_CHOICES]