def merge_entities(entities):
    """Merge and clean NER results."""
    merged = []
    for entity in entities:
        tag = entity['entity_group']
        score = entity['score']
        word = entity['word']

        if tag not in ['ORG', 'PER'] or score < 0.9 or len(word.strip()) < 3:
            continue

        merged_entity = word.replace(" - ", "-")
        if len(merged_entity.split()) > 1 or len(merged_entity) > 6:
            merged.append((merged_entity, tag))
    return merged