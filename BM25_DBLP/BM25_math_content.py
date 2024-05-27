import re
from elasticsearch import Elasticsearch
import warnings
import multiprocessing
import pandas as pd
import subprocess


def text_to_the_es(es, data, title, art_id, sorted_fos_string): # Process lines in the Dataset
    text = ' '.join(data['InvertedIndex'].keys()) # Make string out of text 
    doc_data = {
        "content": text,
        "fos": sorted_fos_string
    }
    es.index(index="bm25_rec_text_and_math_content", id=art_id, body=doc_data) # Add data into the Elasticsearch
                

def process_line(line, i, es): # Process lines in the Dataset
    data = pd.read_json(line, lines=True) # Read line
    if 'indexed_abstract' in data and 'fos' in data: # Preprocessing data
        data.dropna(subset=['indexed_abstract'], inplace=True)
        data['fos'] = data['fos'].apply(lambda x: ', '.join([field['name'].lower() for field in x]))
        sorted_fos_names = data['fos'].str.split(', ').explode().unique()
        sorted_fos_string = ', '.join(sorted(sorted_fos_names))
        data.apply(lambda row: text_to_the_es(es, row['indexed_abstract'], row['title'], row['id'], sorted_fos_string), axis=1) # Process lines in the Dataset


def run_with_timeout(line, i, es): # Process lines in the Dataset
    timeout = 5  # Max execution time
    process = multiprocessing.Process(target=process_line, args=(line, i, es)) # Process lines in the Dataset
    process.start()
    process.join(timeout)
    
    if process.is_alive():
        print(f"Iteration execution time exceeded {row.name}. Stop.")
        process.terminate()


def main():
    warnings.filterwarnings("ignore", message="The 'body' parameter is deprecated and will be removed in a future version.")
    # Connecting to the Elasticsearch
    es = Elasticsearch(hosts=["http://localhost:9200"]) 

    # Setting up the algorithm BM25
    bm25_settings_math = {
        "settings": {
            "index": {
                "similarity": {
                    "default": {
                        "type": "BM25"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "content": {
                    "type": "text"
                },
                "fos": {
                    "type": "text"
                }
            }
        }
    }


    # Create index in the BM25
    index_name = "bm25_rec_text_and_math_content"
    es.indices.create(index=index_name, body=bm25_settings_math)

    file_path = "Data/dblp_papers_v11.txt" # Path to the dblp_papers_v11 dataset

    # Read Data line by line
    with open(file_path, 'r') as file:
        line = file.readline()
        while line:
            run_with_timeout(line, i, es) # Process lines in the Dataset
            line = file.readline()
    process_to_calc_rec = subprocess.run(['python3', 'BM25_text_and_math_content_eval.py']) # Evaluation of the results
    process_to_calc_rec = subprocess.run(['python3', 'Results_of_eval.py']) # Evaluation of the results



if __name__ == "__main__":
    main()
