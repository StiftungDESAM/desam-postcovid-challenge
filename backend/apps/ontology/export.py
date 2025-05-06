from .models import OntologyNode, OntologyRelationship
from knowledge.models import LeafNode, ConnectiveNode
from .utils import get_all_outgoing_relationships, get_all_incoming_relationships
import logging
import io,csv
from typing import Dict,List
logger = logging.getLogger(__name__)

def get_metadata_nodes() -> list[OntologyNode]:
    metadata: OntologyNode = OntologyNode.nodes.get(tag = "Metadaten")
    return metadata.children.all()

def get_relationship_field_name(node1: OntologyNode, node2: OntologyNode):
    """
    Returns the name of the field in node1 defining the relationship with node2.
    E.g. if node1 is the Item node and node2 the Metadata node and they have a HAS relationship,
    the result will be "has_metadata".
    node1 must be the parent of node2 and not the other way around.
    """
    relationship: OntologyRelationship = node1.children.relationship(node2)
    return f"{relationship.name.lower()}_{node2.tag.lower()}"

def search_items(metadata_tag: str, value: str, case_insenstive: bool, match_full_text: bool) -> list[ConnectiveNode]:
    item_node: OntologyNode = OntologyNode.nodes.get(tag = "Item")
    metadata_node: OntologyNode = OntologyNode.nodes.get(tag = "Metadaten")
    search_node: OntologyNode = metadata_node.children.get(tag = metadata_tag)
    Item = item_node.node_class

    # Gets the correct search operator based on the search settings.
    if case_insenstive and match_full_text:
        search_operator = "iexact"
    elif case_insenstive and not match_full_text:
        search_operator = "icontains"
    elif not case_insenstive and match_full_text:
        search_operator = "exact"
    else:
        search_operator = "contains"

    item_to_metadata = get_relationship_field_name(item_node, metadata_node)
    metadata_to_search = get_relationship_field_name(metadata_node, search_node)

    # Dynamically constructs the query, e.g. has_metadata__has_header__current_data__value__contains = "Hello, world"
    query = {f"{item_to_metadata}__{metadata_to_search}__current_data__value__{search_operator}": value}
    items = Item.nodes.filter(**query)
    return [result[0] for result in items]

def get_meta_nodes_for_item(item: ConnectiveNode) -> list[LeafNode]:
    # NOTE: Maybe write a function that does this and caches all results to avoid unnecessary database requests.
    # item_node: OntologyNode = OntologyNode.nodes.get(tag = "Item")
    # metadata_node: OntologyNode = OntologyNode.nodes.get(tag = "Metadaten")
    # item_to_metadata = get_relationship_field_name(item_node, metadata_node)
    item_to_metadata = "hat_metadaten"
    metadata: ConnectiveNode = getattr(item, item_to_metadata).get()

    linked_nodes = get_all_outgoing_relationships(metadata)
    return [link.end_node for link in linked_nodes]

def get_answer_count(item: ConnectiveNode):
    item_to_answers = "hat_antwort"
    answers = getattr(item, item_to_answers).all()
    return len(answers)


SEPARATOR_MAP = {
    "COMMA": ",",
    "SEMICOLON": ";",
    "DASH": "-",
    "UNDERSCORE": "_",
    "SLASH": "/",
    "COLON": ":",
    "DOT": ".",
    "BAR": "|",
}
def split_items(text):
    return [item.strip() for item in text.split(',')]

#TODO: Fixen hier liegt der Fehler 
def get_sorted_values(d):
    result = []
    for key in sorted(d.keys()):
        values = d[key]
        result.extend(values)  
    return result

def fetch_data_for_export(itemstring: str, identificator: str):
    
    items = split_items(itemstring)
    
    ontology_item = OntologyNode.nodes.first_or_none(tag="Item")
    knowledge_items = ontology_item.node_class.nodes.filter(uuid__in=items)
    data = {}
    for item in knowledge_items:
        #logger.debug(f"item = {item.uuid}")
        answergroups= {}
        antworten = item.hat_antwort.all()
        for antwort in antworten:

            #antworten in antwortgruppen einfügen und sortieren nach value der antwortgruppe
            rels = get_all_incoming_relationships(antwort)
            
            answer_group_rel = next((rel for rel in rels if rel.start_node.tag == "Antwortgruppe"), None)
            item_rel = next((rel for rel in rels if rel.start_node.tag == "Item"), None)
            antwortgruppe = answer_group_rel.start_node.hat_reihenid.get_or_none(tag="ReihenID")
            row_identificator = None
            
            if identificator == "META_ROW_ID":
                row_identificator = int(antwortgruppe.current_data.get().value)
            else:
                meta_data = item_rel.start_node.hat_metadaten.get()
                meta_data_rels = get_all_outgoing_relationships(meta_data)
                row_identificator = next((rel.end_node for rel in meta_data_rels if rel.end_node.tag == identificator), None).current_data.get().value
                
            if(row_identificator in answergroups):
                answergroups[row_identificator].append(antwort.current_data.get().value)
            else:
                answergroups[row_identificator]=[antwort.current_data.get().value]

        for key in sorted(answergroups.keys()):
            if key in data:
                data[key].extend(answergroups[key])
            else:
                data[key] = list(answergroups[key])
    return data

def convert_value(value):
    try:
        return int(value)
    except ValueError:
        return value


def convert_dict_values(data: Dict[str, List]) -> Dict[str, List]:
    #logger.debug(f"data is this {data}")
    result = {}
    for key, value_list in data.items():
        result[key] = [convert_value(value) for value in value_list]
    return result

def generate_file_from_data(name: str, typ: str, data: dict, separator: str):
    sep = SEPARATOR_MAP.get(separator.upper(), ",")
    #logger.debug("generate file")
    if typ.lower() == "json":
        # Daten direkt in json (TODO:passt format so?)
        data = convert_dict_values(data)
        #content = json.dumps(data, ensure_ascii=False, indent=2)
        filename = f"{name}.json"
        content= data
        #mode = "w"
        #encoding = "utf-8"
        logger.debug(f"json content = {content}")
        

    elif typ.lower() == "csv":
        output = io.StringIO()
        data = convert_dict_values(data)
        # Keys == CSV Header rauslöschen falls dumm
        fieldnames = list(data.keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=sep,lineterminator='\r\n')
        writer.writeheader()

        # Max Länge der Listen finden (falls daten nicht alle gleich lang)
        max_length = max(len(values) for values in data.values())

        for i in range(max_length):
            row = {}
            for key in fieldnames:
                values = data.get(key, [])
                row[key] = values[i] if i < len(values) else ""
            writer.writerow(row)

        content = output.getvalue()
        output.close()

    else:
        logger.debug("raised erorr")
        raise ValueError("Unsupported file type")

    # Datei schreiben (wird gerade local gespeichert. wo soll die hin? Data Schema also medienpfad oder nur content schicken?)
    #with open(filename, mode, encoding=encoding) as f:
    #    f.write(content)

    #print(f"Datei '{filename}' wurde erfolgreich erstellt.")
    return content