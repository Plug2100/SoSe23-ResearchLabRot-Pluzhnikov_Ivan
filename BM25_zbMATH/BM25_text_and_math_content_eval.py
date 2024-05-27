import re
from elasticsearch import Elasticsearch
import warnings
import multiprocessing
import pandas as pd
import os
import sys


def BM25_search_math(es, text, df, text_source):
    # Line preprocessing
    data = list(text.split(","))
    data = [x for x in data if x != '' and x != '\n']
    id_for_which_rec = data[0] # Id of the document for which we are building recommendations.
    list_of_ids = df['de'].values

    # Look for the perfect recommendations
    good_recommendations_all = data[1:]
    good_recommendations = []
    for i in good_recommendations_all:
        if int(i) in df['de'].values:
            good_recommendations.append(i)
    if(len(good_recommendations) == 0):
        return 0

    # Check if the document for which we are building recommendations is in the dataset.
    if int(id_for_which_rec) not in df['de'].values:
        return 0

    # Query based on id to receive text of the document
    search_query = {
        "query": {
            "ids": {
                "values": [id_for_which_rec]
            }
        },
        "size": 1
    }
    # Executing a search query
    index_name = "bm25_zbmath_content_" + text_source
    search_results = es.search(index=index_name, body=search_query)
    text = search_results['hits']['hits'][0]['_source']['content']

    # Search query using BM25 and size restriction to get recommendations
    search_query = {
        "query": {
            "match": {
                "content": text
            }
        },
        "size": 15
    }
    # Executing a search query.
    search_results = es.search(index=index_name, body=search_query)
    potential_recommendations = []
    for hit in search_results["hits"]["hits"]:
        ID = hit['_id']
        if(ID != id_for_which_rec and len(potential_recommendations) < 10):
            potential_recommendations.append(ID) # Add potential recommendations

    # Calculate precision and recall for top-5 recommendations
    top5_potential = potential_recommendations[:5]
    top5_precision = len(set(top5_potential).intersection(good_recommendations)) / len(top5_potential)
    top5_recall = len(set(top5_potential).intersection(good_recommendations)) / len(good_recommendations)

    # Calculate precision and recall for top-10 recommendations
    top10_potential = potential_recommendations[:10]
    top10_precision = len(set(top10_potential).intersection(good_recommendations)) / len(top10_potential)
    top10_recall = len(set(top10_potential).intersection(good_recommendations)) / len(good_recommendations)

    # Create or open the file for writing results
    with open('Data/precision_recall_results.txt', 'a') as file:
        # Write precision and recall as a single line
        file.write(f"{top5_precision:.5f} {top5_recall:.5f} {top10_precision:.5f} {top10_recall:.5f}\n")


def run_with_timeout(line, es, df, text_source):
    timeout = 5  # Maximum iteration execution time in seconds
    
    process = multiprocessing.Process(target=BM25_search_math, args=(es, line, df, text_source)) # Process line of Data.
    process.start()
    process.join(timeout)
    
    if process.is_alive(): # Break if process taking too much time.
        process.terminate()


def main():
    warnings.filterwarnings("ignore", message="The 'body' parameter is deprecated and will be removed in a future version.")
    # Read Input
    file_path = sys.argv[1]
    text_source = sys.argv[2]

    # Read and preprocess Data
    df = pd.read_csv(file_path)
    df = df.dropna(subset=[text_source])

    # Delete previous results
    if os.path.exists('Data/precision_recall_results.txt'):
        os.remove('Data/precision_recall_results.txt')

    # Connecting to the Elasticsearch
    index_name = "bm25_zbmath_content_" + text_source
    es = Elasticsearch(hosts=["http://localhost:9200"]) 


    file_path = "Data/recommendationPairs.csv" # Path to the Gold Standart Recommendations of the zbMATH. Contact https://github.com/AnkitSatpute to receive.

    # Process Data line by line
    with open(file_path, 'r') as file:
        line = file.readline()
        while line:
            run_with_timeout(line, es, df, text_source)
            line = file.readline()


if __name__ == "__main__":
    main()
