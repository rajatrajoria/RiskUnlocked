import re
from entity_extraction import merge_entities
from entity_classification import classify_entity
from entity_enrichment import query_gleif, map_iso3166_country
from risk_scoring import is_pep
from transformers import pipeline

def process_transaction(transaction):
    if isinstance(transaction, dict):
        txn_id = transaction.get("Transaction ID", "Unknown")
        sender = transaction.get("Payer Name") or transaction.get("Sender Name")
        receiver = transaction.get("Receiver Name")
        raw_text = transaction.get("Transaction Details")
    else:
        raw_text = transaction
        txn_pattern = r"Transaction ID:\s*(\S+)"
        payer_pattern = r"Payer\s*Name:\s*\"([^\"]+)\""
        receiver_pattern = r"Receiver\s*Name:\s*\"([^\"]+)\""
        txn_match = re.search(txn_pattern, transaction)
        payer_match = re.search(payer_pattern, transaction)
        receiver_match = re.search(receiver_pattern, transaction)
        txn_id = txn_match.group(1) if txn_match else "Unknown"
        sender = payer_match.group(1) if payer_match else None
        receiver = receiver_match.group(1) if receiver_match else None
    
    # --- Run NER on the unstructured text ---
    ner = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)
    ner_unstructured = ner(raw_text)
    unstructured_entities = merge_entities(ner_unstructured)

    # --- Run NER on sender and receiver separately ---
    # Here we assume the NER pipeline returns a list; we take the first entity if available.
    sender_entity = None
    if sender:
        ner_sender = ner(sender)
        if isinstance(ner_sender, list) and ner_sender:
            tag = ner_sender[0].get('entity_group')
            if tag not in ['ORG', 'PER']:
                tag = 'ORG'
            sender_entity = (sender, tag)
        else:
            sender_entity = (sender, "ORG")

    receiver_entity = None
    if receiver:
        ner_receiver = ner(receiver)
        if isinstance(ner_receiver, list) and ner_receiver:
            tag = ner_receiver[0].get('entity_group')
            if tag not in ['ORG', 'PER']:
                tag = 'ORG'
            receiver_entity = (receiver, tag)
        else:
            receiver_entity = (receiver, "ORG")

    # --- Combine structured (sender, receiver) and unstructured entities ---
    combined_entities = []
    if sender_entity:
        combined_entities.append(sender_entity)
    if receiver_entity:
        combined_entities.append(receiver_entity)
    for ent in unstructured_entities:
        if ent[0] not in [sender, receiver]:
            combined_entities.append(ent)

    # Deduplicate based on (name, tag)
    combined_entities = list({(name, tag) for name, tag in combined_entities})

    # --- Separate entities by NER tag ---
    per_entities = [name for name, tag in combined_entities if tag == "PER"]
    org_entities = [name for name, tag in combined_entities if tag == "ORG"]

    # --- Classify all entities and calculate overall confidence ---
    classified_entities, countries = [], []
    total_score = 0.0
    for name, tag in combined_entities:
        if tag == 'ORG':
            classification = classify_entity(name)
            sender_gleif_data = query_gleif(name)
            countrycode = sender_gleif_data.get("attributes", {}).get("entity", {}).get("legalAddress", {}).get("country", "Unknown")
            country = map_iso3166_country(countrycode).get("attributes", {}).get("name", "Unknown")
            countries.append(country)
        if tag == 'PER':
            entity_type = 'Individual'
            evidence = None
            if is_pep(name):
                entity_type = 'PEP'
                evidence = 'OpenSanctions'
            classification = {
                'sequence': name,
                'label': entity_type,
                'score': 0.95,
                'supporting_evidence': evidence
            }
            countries.append("Individual")
        classified_entities.append({
            "Extracted Entity": classification["sequence"],
            "Entity Type": classification["label"],
            "Supporting Evidence": classification["supporting_evidence"],
            "Confidence Score": classification["score"]
        })
        total_score += classification["score"]

    overall_confidence = total_score / len(classified_entities) if classified_entities else 0.0
    final_output = {
        "Transaction ID": txn_id,
        "Extracted Entity": [item["Extracted Entity"] for item in classified_entities],
        "Entity Type": [item["Entity Type"] for item in classified_entities],
        "Supporting Evidence": [item["Supporting Evidence"] for item in classified_entities],
        "Confidence Score": round(overall_confidence, 2),
        "Countries": countries
    }
    return final_output