from pymongo import MongoClient
import pandas as pd
import openai
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Set up OpenAI API key
OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY", "your_API_key")
openai.api_key = OPENAI_API_KEY


def connect_to_mongodb():
    client = MongoClient(
        '<your_cluster_uri>')
    db = client['internship']
    collection = db['customer_qna']
    return collection


def load_csv_to_mongodb(csv_file_path, collection):
    # Read CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Convert DataFrame to a list of dictionaries
    data = df.to_dict(orient='records')

    # Insert data into MongoDB collection
    collection.insert_many(data)

    print(f"Inserted {len(data)} records into the collection.")


def openai_embed(query, model="text-embedding-ada-002"):
    try:
        response = openai.embeddings.create(input=[query], model=model)
        embeddings = response.data[0].embedding
        print(f"Created embedding for query: {query}")
        return embeddings
    except Exception as e:
        print(f"Error creating embedding: {e}")
        return None





def store_embedding_and_answer(collection, question, embedding, answer, relevance):
    collection.update_one(
        {'Question': question},
        {'$set': {'Embedding': embedding, 'Answer': answer, 'Relevance': relevance}},
        upsert=True
    )

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
        results = list(collection.aggregate(pipeline))  # Convert cursor to list immediately
        return results
    except Exception as e:
        print(f"Error during vector search: {e}")
        return None





def remove_relevance_field(collection):
    result = collection.update_many({}, {'$unset': {'Relevance': ''}})
    #print(f"Matched {result.matched_count} documents and modified {result.modified_count} documents.")

def create_embeddings_for_all_questions(collection):
    cursor = collection.find({})
    for item in cursor:
        question = item['Question']
        answer=item['Answer']
        if 'Embedding' not in item or item['Embedding'] is None:
            embedding = openai_embed(question)
            if embedding:
                store_embedding_and_answer(collection, question, embedding,answer,1)
                print(f"Stored embedding for question: {question}")
            else:
                print(f"Failed to create embedding for question: {question}")



#Below code was run update the embeddings of the given database initially
# if __name__ == '__main__':
#     collection=connect_to_mongodb()
#     #load_csv_to_mongodb("/Users/sainikhita/Desktop/Intern requirements/Project/backend/customer_queries.csv",collection)
#     create_embeddings_for_all_questions(collection)
