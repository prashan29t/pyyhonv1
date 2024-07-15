import json
from flask import Flask, request, jsonify
import spacy

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

app = Flask(__name__)

def extract_profile_info(description):
    doc = nlp(description)
    
    profile_info = {
        'name': None,
        'job_title': None,
        'company': None,
        'location': None
    }
    
    # Extract entities
    for ent in doc.ents:
        if ent.label_ == 'PERSON' and not profile_info['name']:
            profile_info['name'] = ent.text
        elif ent.label_ == 'ORG' and not profile_info['company']:
            profile_info['company'] = ent.text
        elif ent.label_ == 'GPE' and not profile_info['location']:
            profile_info['location'] = ent.text

    # Heuristic to infer job title
    tokens = [token.text for token in doc]
    job_title_tokens = []
    if '·' in tokens:
        index = tokens.index('·')
        if index + 1 < len(tokens):
            job_title_tokens.append(tokens[index + 1])
            if index + 2 < len(tokens) and tokens[index + 2] != '·':
                job_title_tokens.append(tokens[index + 2])

    # Additional heuristic for job titles
    job_title_keywords = ['Director', 'Manager', 'Engineer', 'Consultant', 'Specialist', 'Coordinator', 'Executive', 'Head', 'Lead']
    for token in doc:
        if token.text in job_title_keywords and not profile_info['job_title']:
            job_title_index = tokens.index(token.text)
            job_title_tokens = tokens[job_title_index - 1:job_title_index + 2]
            profile_info['job_title'] = ' '.join(job_title_tokens)

    profile_info['job_title'] = ' '.join(job_title_tokens).strip()

    # Ensure name does not include job title
    if profile_info['name']:
        profile_info['name'] = profile_info['name'].split('-')[0].strip()

    return profile_info

@app.route('/extract-profile', methods=['POST'])
def extract_profile():
    data = request.get_json()
    description = data.get('description', '')
    if not description:
        return jsonify({'error': 'No description provided'}), 400
    
    info = extract_profile_info(description)
    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True)
