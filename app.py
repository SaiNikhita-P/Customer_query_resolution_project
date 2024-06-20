

from flask import Flask, request, render_template, redirect
import numpy as np
from db import connect_to_mongodb, openai_embed, store_embedding_and_answer


app = Flask(__name__)

collection = connect_to_mongodb()

def question_exists(collection, question):
    return collection.find_one({'Question': question}) is not None

def vector_search(collection, query_embedding, num_candidates=5, limit=3):
    pipeline = [
        {
            "$vectorSearch": {
                "index": "<name of the index>",
                "path": "Embedding",
                "queryVector": query_embedding,
                "numCandidates": num_candidates,
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 0,
                "Question": 1,
                "Answer": 1,
                "score": {
                    "$meta": "vectorSearchScore"
                }
            }
        }
    ]

    try:
        results = list(collection.aggregate(pipeline))
        if results and results[0]['score'] < 0.90:
            return None
        return results
    except Exception as e:
        print(f"Error during vector search: {e}")
        return None

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    if request.method == 'GET':
        return render_template('index1.html')

    new_question = request.form.get('question')

    if not new_question:
        return redirect("/", code=302)

    if question_exists(collection, new_question):
        doc = collection.find_one({'Question': new_question})
        return render_template('index1.html', answers=[doc], question=doc['Question'], score=1, is_new=False, question_exists=True)

    new_question_embedding = openai_embed(new_question)
    if new_question_embedding is None:
        return render_template('index1.html', answers=[], question=new_question, error="Error creating embedding. Please try again.")

    try:
        similar_docs = vector_search(collection, new_question_embedding)

        if not similar_docs:
            return render_template('index1.html', answers=[], question=new_question, error="No relevant answer found. Please provide an answer:")

        store_embedding_and_answer(collection, new_question, new_question_embedding, similar_docs[0]['Answer'], similar_docs[0]['score'])
        return render_template('index1.html', answers=similar_docs, question=new_question)
    except Exception as e:
        print(f"Error during vector search: {e}")
        return render_template('index1.html', answers=[], question=new_question, error="Error during vector search. Please try again.")

@app.route('/submit_answer', methods=['POST', 'GET'])
def submit_answer():
    if len(request.form) == 0:
        return redirect("/", code=302)

    question = request.form['question']
    answer = request.form['answer']

    if not question_exists(collection, question):
        embedding = openai_embed(question)
        if embedding:
            store_embedding_and_answer(collection, question, embedding, answer, 1)
    else:
        # Update the answer and set a default relevance score
        collection.update_one(
            {'Question': question},
            {'$set': {'Answer': answer, 'Relevance': 1}}
        )

    # Retrieve all answers for the question, including relevance scores
    answers = list(collection.find({'Question': question}))

    # Assuming relevance is stored in 'Relevance' field and adjusting template logic accordingly
    for answer_doc in answers:
        if 'Relevance' not in answer_doc:
            answer_doc['Relevance'] = 1

    return render_template('index1.html', answers=answers, question=question, is_new=False)

if __name__ == '__main__':
    app.run(debug=True)

