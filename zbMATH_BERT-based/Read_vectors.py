import os
import pandas as pd
import chromadb
import sys


def process_line(line, collection, df, path_to_results):
    # Preprocessing
    data = list(line.split(","))
    data = [x for x in data if x != '' and x != '\n']
    id_of_our_doc = data[0] # Id of the document for which we build the recommendations
    if int(id_of_our_doc) not in df['de'].values:
        return 0

    # Receive Ideal Recommendations
    good_recommendations_all = data[1:]
    good_recommendations = []
    for i in good_recommendations_all:
        if int(i) in df['de'].values:
            good_recommendations.append(i)
    if(len(good_recommendations) == 0):
        return 0
    
    # Receive recommendations from the Collection
    responce = collection.get(ids=[str(id_of_our_doc)], include=['embeddings'])
    embedding = responce['embeddings'][0]
    ans = collection.query(
        query_embeddings=[embedding],
        n_results=11 
    )
    potential_recommendations = ans['ids'][0][1:] # Delete document for which we are building recommendations itself
    
    # Calculate precision and recall for top-5 recommendations
    top5_potential = potential_recommendations[:5]
    top5_precision = len(set(top5_potential).intersection(good_recommendations)) / len(top5_potential)
    top5_recall = len(set(top5_potential).intersection(good_recommendations)) / len(good_recommendations)

    # Calculate precision and recall for top-10 recommendations
    top10_potential = potential_recommendations[:10]
    top10_precision = len(set(top10_potential).intersection(good_recommendations)) / len(top10_potential)
    top10_recall = len(set(top10_potential).intersection(good_recommendations)) / len(good_recommendations)
    with open(path_to_results, 'a') as file:
        # Write precision and recall as a single line
        file.write(f"{top5_precision:.5f} {top5_recall:.5f} {top10_precision:.5f} {top10_recall:.5f}\n")


def main():
    chroma_client = chromadb.PersistentClient(path=sys.argv[1]) # Connect to the Database
    collection = chroma_client.get_collection(name="embedding") # Connect to the Collection

    path_to_results = 'Data/precision_recall_results.txt'
    if os.path.exists(path_to_results): # Clean previous results
        os.remove(path_to_results)

    file_path = "Data/recommendationPairs.csv" # Path with the Ideal Recommendations. Contact authors of the  
    file_path_existing = sys.argv[3] # zbMATH Dataset. To receive, contact https://github.com/AnkitSatpute
    df = pd.read_csv(file_path_existing)
    df = df.dropna(subset=[sys.argv[2]]) # Preprocessing
    with open(file_path, 'r') as file: # Evaluate recommendations
        line = file.readline()
        while line:
            process_line(line, collection, df, path_to_results)
            line = file.readline()


if __name__ == "__main__":
    main()
