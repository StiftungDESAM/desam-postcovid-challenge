from ontology.models import OntologyNode
from study.models import CodeBook

def get_data_rows_for_codebook(codebook: CodeBook):
    ontology_study_id = OntologyNode.nodes.first_or_none(tag="StudienID")
    study_id = ontology_study_id.node_class.nodes.get(current_data__value = str(codebook.study.id))[0]
    ontology_answer_group = OntologyNode.nodes.first_or_none(tag="Antwortgruppe")
    answer_groups = ontology_answer_group.node_class.nodes.filter(graph_id=study_id.graph_id)
    
    data_rows = []

    unordered_answers = []
    unordered_column_names = []
    for answer_group in answer_groups:
        ontology_codebook = OntologyNode.nodes.first_or_none(tag="Fragebogen")
        knowledge_codebooks = ontology_codebook.node_class.nodes.all()
        
        found_codebook = None
        for cb in knowledge_codebooks:
            if cb.hat_fragebogenid.get_or_none(tag="FragebogenID").current_data.get().value == str(codebook.id):
                found_codebook = cb
                break
        
        items = found_codebook.hat_item.all()
        answers = list(answer_group.hat_antwort.filter(tag="Antwort"))
        answer_uuids = {answer.uuid for answer in answers}
        mapped_answers = list()
        
        for item in items:
            all_answers = item.hat_antwort.all() 
            idx = int(item.hat_spaltenid.get(tag="SpaltenID").current_data.get().value)
            
            mapped_answers.append(dict(
                idx=idx,
                answers=[answer for answer in all_answers if answer.uuid in answer_uuids]
            ))
            
            unordered_column_names.append(dict(
                idx=idx,
                name= item.hat_metadaten.get().hat_feldname.get().current_data.get().value,
            ))
        
        sorted_answers = sorted(mapped_answers, key=lambda x: x['idx'])
        
        try:
            idx = int(answer_group.hat_reihenid.get().in_review.get().value)
        except:
            idx = int(answer_group.hat_reihenid.get().current_data.get().value)
        
        try:
            answers = [answer.in_review.get().value for item in sorted_answers for answer in item['answers']]
        except:
            answers = [answer.current_data.get().value for item in sorted_answers for answer in item['answers']]
        
        unordered_answers.append(dict(
            idx=idx,
            answers=answers
        ))
    
    sorted_column_names = sorted(unordered_column_names, key=lambda x: x['idx'])
    
    answers = []
    seen = set()
    for col in sorted_column_names:
        name = col["name"]
        if name not in seen:
            answers.append(name)
            seen.add(name)
            
    unordered_answers.append(dict(
        idx=-1,
        answers=answers
    ))
    return data_rows + [answers["answers"] for answers in sorted(unordered_answers, key=lambda x: x['idx'])]