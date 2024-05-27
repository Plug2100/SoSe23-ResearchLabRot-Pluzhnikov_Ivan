import re
from elasticsearch import Elasticsearch
import warnings
import multiprocessing
import pandas as pd
import subprocess


def text_to_the_es(es, text, title, keyword, art_id, msc, text_sourse): # Process lines in the Dataset
    # Data preprocessing
    if type(keyword) != float:
        keyword = keyword [1:-1]
        keyword = keyword.replace(",", "")
        keyword = keyword.replace("'", "")
    if(type(msc) != float and msc[0] == "["):
        msc = msc [1:-1]
    if type(msc) != float:     
        msc = msc.replace(",", "")
    if type(text) != float: 
        if(text[:9] == 'Summary: '):
            text = text[9:]
    # Content to write into Elasticsearch
    if(text_sourse == "msc"):
        doc_data = {
            "content": msc
        }
    if(text_sourse == "keyword"):
        doc_data = {
            "content": keyword
        }
    if(text_sourse == "text"):
        doc_data = {
            "content": text
        }
    if(text_sourse == "title"):
        doc_data = {
            "content": title
        }
    es.index(index="bm25_zbmath_content_" + text_sourse, id=art_id, body=doc_data) # Add data into the Elasticsearch


def run_with_timeout(row, text_sourse, es): # Process lines in the Dataset
    timeout = 10  # Max execution time
    process = multiprocessing.Process(target=text_to_the_es, args=(es, row['text'], row['title'], row['keyword'], row['de'], row['msc'], text_sourse)) # Process lines in the Dataset
    process.start()
    process.join(timeout)    
    if process.is_alive():
        print(f"Iteration execution time exceeded {row.name}. Stop.")
        process.terminate()


def main():
    for text_sourse in ["msc", "text", "title", "keyword"]: # Process all the text sources
        # Connecting to the Elasticsearch
        es = Elasticsearch(hosts=["http://localhost:9200"])  # Укажите свои параметры подключения
        warnings.filterwarnings("ignore", message="The 'body' parameter is deprecated and will be removed in a future version.")

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
                    "zbmath_id": {
                        "type": "text"
                    }
                }
            }
        }


        # Path to the zbMATH dataset
        file_path = 'Data/out.csv'
        df = pd.read_csv(file_path)
        # Preprocessing
        df = df.dropna(subset=[text_sourse])

        # Create index in the BM25
        index_name = "bm25_zbmath_content_" + text_sourse 
        es.indices.create(index=index_name, body=bm25_settings_math) 

        # Process lines in the Dataset
        df.apply(lambda row: run_with_timeout(row, text_sourse, es), axis=1)
        process_to_calc_rec = subprocess.run(['python3', 'BM25_text_and_math_content_eval.py', file_path, text_sourse]) # Evaluation of the results
        process_to_calc_rec = subprocess.run(['python3', 'Results_of_eval.py']) # Evaluation of the results


if __name__ == "__main__":
    main()
    
