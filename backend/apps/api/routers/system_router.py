from api.transactions import TransactionRouter

from neomodel import db

from api import schema
from authentication.models import CustomUser
from ontology.models import OntologyNode
from reviewer.models import Review, UploadTypeChoices

from collections import namedtuple
from typing import List

import logging

logger = logging.getLogger(__name__)
router = TransactionRouter()

# TODO: Move functions from these endpoints to their own module.
def get_study_count():
    # NOTE: Currently only studies with an accepted ontology review are counted.
    accepted_study_reviews = Review.objects.filter(study__isnull = False, details__status = "ACCEPTED", upload_type = UploadTypeChoices.UPLOAD_ONTOLOGY.value)
    return accepted_study_reviews.distinct("study").count()

def get_datapoint_count():
    # NOTE: Only answers are currently counted as data points.
    answer_node: OntologyNode = OntologyNode.nodes.get(tag = "Antwort")
    answers_with_data = answer_node.node_class.nodes.filter(is_verified = True).has(current_data = True)
    return len(answers_with_data)

def get_participant_count():
    participant: OntologyNode = OntologyNode.nodes.get(tag = "Teilnehmer")
    verified_participants = participant.node_class.nodes.filter(is_verified = True)
    return len(verified_participants)

def get_user_count():
    active_users = CustomUser.objects.filter(is_active = True)
    return active_users.count()

@router.get(
    "/stats",
    summary = "Returns stats about the system",
    description = "This endpoint returns stats about the system including number of studies, amount of datapoints, amount of participants and signed up users",
    auth = None,
    response = {200: List[schema.SystemStats]}
)
def system_stats(request):
    logger.info(f"Getting system stats.")
    Stats = namedtuple("Stats", ["type", "amount"])
    return [
        Stats("AMOUNT_STUDIES", get_study_count()),
        Stats("AMOUNT_DATAPOINTS", get_datapoint_count()),
        Stats("AMOUNT_PARTICIPANTS", get_participant_count()),
        Stats("AMOUNT_USERS", get_user_count())
    ]


def evaluate_query(key: str, query: str, results: dict):
    query_result = db.cypher_query(query)[0]
    for row in query_result:
        graph_id = row[0]
        value = row[1]
        
        if graph_id not in results:
            results[graph_id] = {"id": graph_id}
        results[graph_id][key] = value

def get_n_biggest_studies(data: list[dict], n: int):
    filtered = [obj for obj in data if 'datapoints' in obj]
    sorted_items = sorted(filtered, key=lambda item: item['datapoints'], reverse=True)
    return sorted_items[:n]


@router.get(
    "/highlights",
    summary = "Returns a number of highlighted studies",
    description = "This endpoint returns a number of highlighted studies. The amount specifies how many studies are returned. The studies with the most amount of datapoints are returned first",
    auth = None,
    response = {200: List[schema.HighlightedStudy]}
)
def system_highlights(request, amount: int):
    # To avoid making big queries on every single study subsequently, they're made in batch.
    query_results = {}
    queries = {
        "questionnaires": "MATCH (n:Fragebogen {is_verified: true}) RETURN n.graph_id, COUNT(n)",
        "questions": "MATCH (n:Item {is_verified: true}) RETURN n.graph_id, COUNT(n)",
        "participants": "MATCH (n:Teilnehmer {is_verified: true}) RETURN n.graph_id, COUNT(n)",
        "datapoints": "MATCH (n:Antwort {is_verified: true})-[:CURRENT]->(:DataNode) RETURN n.graph_id, COUNT(n)",
        "name": "MATCH (:Studienname)-[:CURRENT]->(data:DataNode) RETURN data.graph_id, data.value"
    }

    # This compiles the results of all queries into a dict, ordered by study_id/graph_id
    for key, query in queries.items():
        evaluate_query(key, query, query_results)

    return get_n_biggest_studies(query_results.values(), amount)