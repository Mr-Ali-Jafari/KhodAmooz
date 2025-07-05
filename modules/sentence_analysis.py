import spacy

nlp = spacy.load("en_core_web_sm")

def analyze_sentence(text):
    doc = nlp(text)
    result = []
    for token in doc:
        result.append({
            "word": token.text,
            "pos": token.pos_,
            "tag": token.tag_ 
        })
    return result
