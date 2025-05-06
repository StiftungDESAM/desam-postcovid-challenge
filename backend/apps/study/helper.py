import inspect
from typing import Dict
from graph_migrations.studies import generate_tag_name
from study.models import CodeBook, CodeBookColumn, Study
from ontology.utils import get_all_outgoing_relationships
from ontology.models import OntologyNode

import logging
logger = logging.getLogger(__name__)

def get_study_from_knowledge_graph(id: int):
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

            if str(study_id) == str(id):
                found_study = study
                break
        except:
            logger.exception(f"Error processing study with UUI {study.uuid}.")
            continue
        
    return found_study, id

def get_code_books_for_study(study: OntologyNode, id: int):
    code_books = []
    data_query = study.hat_datenerhebung.filter(tag="Datenerhebung")
    for query in data_query:
        code_books += list(query.hat_fragebogen.filter(tag="Fragebogen"))
    
    
    return code_books, id
        


def get_id_of_code_book(code_book: OntologyNode):
    return code_book.hat_fragebogenid.get_or_none(tag="FragebogenID").current_data.get().value

def get_name_of_code_book(code_book: OntologyNode):
    return code_book.hat_fragebogenname.get_or_none(tag="Fragebogenname").current_data.get().value

def get_data_quality_check_config_for_code_book(code_book: OntologyNode):
    return code_book.hat_qualitaetspruefung.get_or_none(tag="Qualitaetspruefung")

def get_meta_for_code_book(code_book: OntologyNode, codebook_id: int):
    study = Study.objects.get(id=code_book._study_id)
    codebook = study.codebooks.get(id=codebook_id)
    return codebook.columns.all()
  
def get_columns_for_code_book(code_book: OntologyNode):
    return list(code_book.hat_item.filter(tag="Item"))

def get_rows_for_code_book(code_book: OntologyNode):
    return list(code_book.hat_antwortgruppe.filter(tag="Antwortgruppe"))
    
def get_data_quality_check_config_values(dqcc: OntologyNode):  
    return {
        "empty_columns": dqcc.hat_leerespalten.get_or_none(tag="LeereSpalten").current_data.get().value,
        "empty_rows": dqcc.hat_leerezeilen.get_or_none(tag="LeereZeilen").current_data.get().value,
        "empty_values": dqcc.hat_leerewerte.get_or_none(tag="LeereWerte").current_data.get().value,
        "value_type": dqcc.hat_datentyp.get_or_none(tag="Datentyp").current_data.get().value,
        "value_range_min": dqcc.hat_minimum.get_or_none(tag="Minimum").current_data.get().value,
        "value_range_max": dqcc.hat_maximum.get_or_none(tag="Maximum").current_data.get().value,
        "value_required": dqcc.hat_benoetigtqualitaetspruefung.get_or_none(tag="BenoetigtQualitaetspruefung").current_data.get().value,
        "value_mapping": dqcc.hat_auswahlmoeglichkeiten.get_or_none(tag="Auswahlmoeglichkeiten").current_data.get().value,
        "mapping_separator": dqcc.hat_trennzeichenauswahlmoeglichkeiten.get_or_none(tag="TrennzeichenAuswahlmoeglichkeiten").current_data.get().value,
        "answer_separator": dqcc.hat_trennzeichenantworten.get_or_none(tag="TrennzeichenAntworten").current_data.get().value,
    }

def get_row_idx_by_answer_group(answer_group: OntologyNode):
    return int(answer_group.hat_reihenid.get_or_none(tag="ReihenID").current_data.get().value)
    
def get_row_cells_by_answer_group(answer_group: OntologyNode):
    ontology_codebook = OntologyNode.nodes.first_or_none(tag="Fragebogen")
    knowledge_codebooks = ontology_codebook.node_class.nodes.all()
    
    found_codebook = None
    for codebook in knowledge_codebooks:
        if codebook.hat_fragebogenid.get_or_none(tag="FragebogenID").current_data.get().value == str(answer_group._codebook_id):
            found_codebook = codebook
            break
    
    items = found_codebook.hat_item.all()
    answers = list(answer_group.hat_antwort.filter(tag="Antwort"))
    answer_uuids = {answer.uuid for answer in answers}
    mapped_answers = list()
    
    for item in items:
        all_answers = item.hat_antwort.all() 
        
        mapped_answers.append(dict(
            idx=int(item.hat_spaltenid.get(tag="SpaltenID").current_data.get().value),
            answers=[answer for answer in all_answers if answer.uuid in answer_uuids]
        ))
    
    sorted_answers = sorted(mapped_answers, key=lambda x: x['idx'])
    return [answer.current_data.get().value for item in sorted_answers for answer in item['answers']]
   
def get_column_idx_by_item(item: OntologyNode): 
    return int(item.hat_spaltenid.get_or_none(tag="SpaltenID").current_data.get().value)

def get_column_item_by_item(item: OntologyNode):
    return extract_metadata_dict(item)

def get_column_name_by_item(item: OntologyNode): 
    meta_data = item.hat_metadaten.get_or_none(tag="Metadaten")
    return meta_data.hat_feldname.get_or_none(tag="Feldname").current_data.get().value
    
def get_linked_item_by_item(item: OntologyNode):
    meta_data = item.hat_metadaten.get_or_none(tag="Metadaten")
    linked_item = meta_data.hat_verknuepftesitemid.get_or_none(tag="VerknuepftesItemID")
    
    if linked_item is not None:
        linked_item_uuid = linked_item.current_data.get().value
        
        ontology_item = OntologyNode.nodes.first_or_none(tag="Item")
        matched_item = ontology_item.node_class.nodes.first_or_none(uuid=linked_item_uuid)
        
        return extract_metadata_dict(matched_item)
    else:
        return None
    

def extract_metadata_dict(item):
    meta_data = {
        "id": item.uuid
    }
    
    item_meta = item.hat_metadaten.get_or_none(tag="Metadaten")
    
    if item_meta:
        for rel in get_all_outgoing_relationships(item_meta):
            meta_data[rel.end_node.tag] = rel.end_node.current_data.get().value
    
    return meta_data

def get_assigned_meta_field(column: CodeBookColumn):
    node = OntologyNode.nodes.first_or_none(
        tag=column.assigned_meta_tag if column.assigned_meta_tag is not None else column.header
    )
    
    return node

def get_tag_of_meta_field(column: CodeBookColumn):
    return column.assigned_meta_tag if column.assigned_meta_tag is not None else generate_tag_name(column.header)

def get_rows(column: CodeBookColumn):
    codebook = CodeBook.objects.get(id=column.codebook.id)
    return [row.cells[column.idx] for row in codebook.rows.all()]