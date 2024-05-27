# Research lab rotation

Include experiments for the topic 'Recommender system for scientific documents with mathematical content.'

Used Datasets: https://www.aminer.org/citation - DBLP + Citation v11 (too large to include here).
               Dataset which was provided by Supervisor Ankit Satpute (MathRecGoldStandData https://zenodo.org/records/6448360). Unfortunately I can not add info about recommendations here.

For stoaring data used Chromadb and Elasticsearch.

Results and additional information can be found in the presentation.

The order of program running: 

A) zbMATH + BERT-based models (folder zbMATH_BERT-based): 1) Make_vectors_using_llm 2) Read_vectors 3) Results_of_eval

B) DBLP + BERT-based models (folder DBLP_BERT-based): 1) Make_vectors_using_llm 2) Recommendations_validation 3) Results_of_evaluation

C) zbMATH + BM25 (folder BM25_zbMATH): 1) BM25_code_into_elasticsearch 2) BM25_text_and_math_content_eval 3) Results_of_eval

D) DBLP + BM25 (folder BM25_DBLP): 1) BM25_math_content 2) BM25_text_and_math_content_eval 3) Results_of_eval


Documentation about code:

A) 

    1) Make_vectors_using_llm: serves the purpose of generating embeddings for text data using different pre-trained BERT-based models and evaluating the results. The embeddings are stored in a database, and the evaluation metrics (precision and recall) are written to a file for further analysis.
    
    ---------------------------------------
    
    convert_to_emb_and_save(text, title, id_, keyword, collection, text_sourse, method, tokenizer, model)
    
    Purpose: Converts input text to embeddings using a specified BERT-based model and saves the embeddings to a specified database collection.
    
    Parameters:
    text (str): Abstract of the article.
    
    title (str): Title of the text.
    
    id_ (int): Unique identifier for the text.
    
    keyword (str): Keywords associated with the article.
    
    collection (ChromaDB collection): Database collection to store the embeddings.
    
    text_sourse (str): Source of the text for vector representation ('text', 'title', or 'keyword').
    
    method (str): Method to obtain vectors from the BERT-based model ('pooler_output' or 'mean').
    
    tokenizer (Tokenizer): Tokenizer for the specified BERT-based model.
    
    model (Model): BERT-based model for generating embeddings.
    
    Returns: None
    
    ---------------------------------------
    
    process_line(row, collection, text_sourse, method, tokenizer, model)
    
    Purpose: Processes a row of a DataFrame, extracts relevant information, and calls convert_to_emb_and_save to generate and save embeddings.
    
    Parameters:
    
    row (pandas DataFrame row): Row containing information about the text.
    
    collection (ChromaDB collection): Database collection to store the embeddings.
    
    text_sourse (str): Source of the text for vector representation ('text', 'title', or 'keyword').
    
    method (str): Method to obtain vectors from the BERT-based model ('pooler_output' or 'mean').
    
    tokenizer (Tokenizer): Tokenizer for the specified BERT-based model.
    
    model (Model): BERT-based model for generating embeddings.
    
    Returns: None
    
    ---------------------------------------
    
    main()
    
    Purpose: Main function to execute the entire process, including reading data, choosing BERT-based models, generating embeddings, and evaluating results.

    Also call Read_vectors and Results_of_eval.
    
    Parameters: None
    
    Returns: None
    
    ---------------------------------------


    
    2) Read_vectors: is designed to evaluate the precision and recall of recommendations generated using embeddings stored in a ChromaDB collection. The recommendations are compared against a set of ideal recommendations provided in a CSV file (Data/recommendationPairs.csv). The results, including precision and recall for top-5 and top-10 recommendations, are written to a text file (Data/precision_recall_results.txt).

    process_line(line, collection, df, path_to_results)
    
    Purpose: Processes a line from a file containing recommendations, calculates precision and recall, and writes the results to a specified file.
    
    Parameters:
    
    line (str): Line containing information about recommendations.
    
    collection (ChromaDB collection): Database collection containing embeddings.
    
    df (pandas DataFrame): DataFrame containing information about the documents.
    
    path_to_results (str): Path to the file where precision and recall results will be written.
    
    Returns: None

    ---------------------------------------
    
    main()
    
    Purpose: Main function to execute the entire process, including connecting to the database, reading the ideal recommendations, and evaluating the precision and recall of recommendations.
    
    Parameters: None
    
    Returns: None

    ---------------------------------------

    

    3) Results_of_eval: calculates the average precision and recall values for top-5 and top-10 recommendations based on data stored in a file (Data/precision_recall_results.txt). The script reads precision and recall values from each line, accumulates them, and then calculates the averages.

    Functions
    
    main()
    
    Purpose: Main function to execute the entire process of calculating average precision and recall.
    
    Parameters: None
    
    Returns: None

B)        
    
    1) Make_vectors_using_llm: aims to generate embeddings for text data using the MathBERT model, save the embeddings in a ChromaDB collection, and perform subsequent recommendation validation. The recommendation validation involves running external scripts (Recommendations_validation.py and Results_of_evaluation.py) to evaluate the recommendation results.

    convert_to_emb_and_save(text, id_, collection, model, tokenizer)
    
    Purpose: Converts input text to embeddings using the different BERT models and saves the embeddings to a ChromaDB collection.
    
    Parameters:
    
    text (str): Input text to be converted to embeddings.
    
    id_ (int): Unique identifier for the text.
    
    collection (ChromaDB collection): Database collection to store the embeddings.
    
    model (BertModel): MathBERT model for generating embeddings.
    
    tokenizer (BertTokenizer): Tokenizer for the MathBERT model.
    
    Returns: None

    ---------------------------------------

    process_line(line, collection, model, tokenizer)
  
    Purpose: Processes a line from a JSON file, extracts relevant information, and calls convert_to_emb_and_save to generate and save embeddings.
    
    Parameters:
    
    line (str): Line containing information about the text in JSON format.
    
    collection (ChromaDB collection): Database collection to store the embeddings.
    
    model (BertModel): MathBERT model for generating embeddings.
    
    tokenizer (BertTokenizer): Tokenizer for the MathBERT model.

    ---------------------------------------

    main()
    
    Purpose: Main function to execute the entire process, including reading data, generating embeddings, and running recommendation validation scripts.
    
    Parameters: None
    
    Returns: None

    ---------------------------------------




    2) Recommendations_validation:  processes a dataset (Data/dblp_papers_v11.txt), retrieves embeddings from a ChromaDB collection (EMB_FOR_LLM_COS_DIST), and evaluates the quality of recommendations based on the similarity of the field of study (FOS) between the query document and the recommended documents. The evaluation metrics include precision and recall for both top-5 and top-10 recommendations.

    count_common_elements(row, my_list)
    
    Purpose: Counts the common elements between the FOS of a document and a list.
    
    Parameters:
    
    row (pandas DataFrame row): Row containing information about a document.
    
    my_list (list): List of elements to compare with the FOS of the document.
    
    Returns: Number of common elements.
    
    ---------------------------------------

    process_line(line, collection, df)
    
    Purpose: Processes a line from the dataset, retrieves embeddings, performs recommendations, and evaluates precision and recall metrics.
    
    Parameters:

    line (str): Line containing information about a document in JSON format.
    
    collection (ChromaDB collection): Database collection containing embeddings.
    
    df (pandas DataFrame): DataFrame containing information about the documents.

    ---------------------------------------

    main()

    Purpose: Main function to execute the entire process, including connecting to the database, reading data, processing lines, and evaluating precision and recall.

    Parameters: None

    Returns: None
    
    Returns: None

    ---------------------------------------




    3) Results_of_evaluation:  calculates the average recall and precision metrics based on data stored in the file Data/data_about_good_rec_recall.txt. The file contains information about the quality of recommendations, including recall and precision values for both top-5 and top-10 recommendations.

    main()
    
    Purpose: Main function to execute the entire process of calculating average recall and precision metrics.
    
    Parameters: None
    
    Returns: None

C)

    1) BM25_code_into_elasticsearch: processes a dataset (out.csv), extracts information, and indexes the data into an Elasticsearch instance. It utilizes the BM25 similarity algorithm for indexing. The script then evaluates the results using an external script (BM25_text_and_math_content_eval.py) and outputs the evaluation results using another external script (Results_of_eval.py).

    text_to_the_es(es, text, title, keyword, art_id, msc, text_sourse)
    
    Purpose: Processes lines in the dataset and indexes the data into Elasticsearch.
    
    Parameters:
    
    es (Elasticsearch): Elasticsearch instance.
    
    text (str or float): Text content of the document.
    
    title (str): Title of the document.
    
    keyword (str or float): Keywords associated with the document.
    
    art_id (int): Article ID.
    
    msc (str or float): Mathematical Subject Classification (MSC) codes associated with the document.
    
    text_sourse (str): Source of the text (e.g., "msc", "text", "title", "keyword").
    
    Returns: None

    ---------------------------------------

    run_with_timeout(row, text_sourse, es)

    Purpose: Processes lines in the dataset with a timeout to prevent long-running tasks.
    
    Parameters:
    
    row (pandas DataFrame row): Row containing information about a document.
    
    text_sourse (str): Source of the text (e.g., "msc", "text", "title", "keyword").
    
    es (Elasticsearch): Elasticsearch instance.
    
    Returns: None

    ---------------------------------------

    main()
    
    Purpose: Main function to execute the entire process of indexing data into Elasticsearch, setting up BM25, and evaluating the results.
    
    Parameters: None
    
    Returns: None

    ---------------------------------------




    2) BM25_text_and_math_content_eval: performs a search using the BM25 algorithm in Elasticsearch to find potential recommendations based on a given document's content. It calculates precision and recall metrics for top-5 and top-10 recommendations and writes the results to the file Data/precision_recall_results.txt.


    BM25_search_math(es, text, df, text_source)
      
    Purpose: Processes lines in the dataset, performs a BM25 search in Elasticsearch, and calculates precision and recall metrics for top-5 and top-10 recommendations.
    
    Parameters:
    
    es (Elasticsearch): Elasticsearch instance.
    
    text (str): Text content of the document for which recommendations are being built.
    
    df (pandas DataFrame): DataFrame containing the zbMATH dataset.
    
    text_source (str): Source of the text (e.g., "msc", "text", "title", "keyword").
    
    Returns: None
      
    ---------------------------------------

    run_with_timeout(line, es, df, text_source)
    
    Purpose: Processes lines in the dataset with a timeout to prevent long-running tasks.
    
    Parameters:
    
    line (str): Line of text containing information about a document.
    
    es (Elasticsearch): Elasticsearch instance.
    
    df (pandas DataFrame): DataFrame containing the zbMATH dataset.
    
    text_source (str): Source of the text (e.g., "msc", "text", "title", "keyword").
    
    Returns: None

    ---------------------------------------

    main()
    Purpose: Main function to execute the entire process of searching for potential recommendations, calculating precision and recall metrics, and writing the results to a file.
    
    Parameters: None
    
    Returns: None

    ---------------------------------------




    3) Results_of_eval: calculates the average precision and recall for top-5 and top-10 recommendations based on the data stored in the file Data/precision_recall_results.txt. The script reads this file, which contains precision and recall values for each line, and calculates the averages.

    main()
    
    Purpose: Main function to calculate average precision and recall for top-5 and top-10 recommendations.
    
    Parameters: None
    
    Returns: None

D)

    1) BM25_math_content: processes the lines in the dataset (Data/dblp_papers_v11.txt) and adds data into an Elasticsearch index named bm25_rec_text_and_math_content. It creates an index with BM25 similarity settings and stores document content and field of study (FOS) information. Also start BM25_text_and_math_content_eval and Results_of_eval.

    text_to_the_es(es, data, title, art_id, sorted_fos_string)
    
    Purpose: Process lines in the dataset and add data into the Elasticsearch index.
    
    Parameters:
    
    es (Elasticsearch): Elasticsearch client.
    
    data (pd.Series): Indexed abstract data from the dataset.
    
    title (str): Title of the document.
    
    art_id (int): Article ID.
    
    sorted_fos_string (str): Comma-separated string of sorted field of study names.
    
    Returns: None

    ---------------------------------------

    process_line(line, i, es)

    Purpose: Process lines in the dataset.
    
    Parameters:
    
    line (str): Line from the dataset.
    
    i (int): Index or identifier for the line.
    
    es (Elasticsearch): Elasticsearch client.
    
    Returns: None

    ---------------------------------------

    run_with_timeout(line, i, es)
    
    Purpose: Process lines in the dataset with a timeout.
    
    Parameters:
    
    line (str): Line from the dataset.
    
    i (int): Index or identifier for the line.
    
    es (Elasticsearch): Elasticsearch client.
    
    Returns: None

    ---------------------------------------

    main()
    
    Purpose: Main function to process lines in the dataset, add data to Elasticsearch, and evaluate the results.
    
    Parameters: None
    
    Returns: None
    
    ---------------------------------------




    2) BM25_text_and_math_content_eval:  interacts with Elasticsearch, specifically the bm25_rec_text_and_math_content index, to perform search queries and evaluate recommendations based on common field of study (FOS) elements between documents and their potential recommendations. The script reads a dataset (Data/dblp_papers_v11.txt), processes each line, and performs a BM25 search in Elasticsearch to find relevant recommendations.

    count_common_elements(row, my_list)
    
    Purpose: Calculate the number of common elements between the FOS in a row and a given list.
    
    Parameters:
    
    row (pd.Series): A row from the dataset containing FOS information.
    
    my_list (list): The list of FOS elements to compare against.
    
    Returns: The count of common elements.

    ---------------------------------------

    BM25_search_math(es, text, sorted_fos_string, art_id, df)
    
    Purpose: Perform a BM25 search in Elasticsearch, evaluate recommendations based on common FOS elements, and write the results to a file.
    
    Parameters:
    
    es (Elasticsearch): Elasticsearch client.
    
    text (str): Text content for the BM25 search.
    
    sorted_fos_string (str): Comma-separated string of sorted FOS names.
    
    art_id (int): Article ID for which recommendations are being evaluated.
    
    df (pd.DataFrame): DataFrame containing FOS information for all documents in the dataset.
    
    Returns: None

    ---------------------------------------

    Data_to_str(es, data, title, art_id, sorted_fos_string, df)

    Purpose: Convert data from the dataset to a string for BM25 search and initiate the BM25 search.
    
    Parameters:
    
    es (Elasticsearch): Elasticsearch client.
    
    data (pd.Series): Indexed abstract data from the dataset.
    
    title (str): Title of the document.
    
    art_id (int): Article ID.
    
    sorted_fos_string (str): Comma-separated string of sorted FOS names.
    
    df (pd.DataFrame): DataFrame containing FOS information for all documents in the dataset.
    
    Returns: None

    ---------------------------------------

    process_line(es, line, i, df)
    
    Purpose: Process a line from the dataset, converting it to a DataFrame and initiating the BM25 search.
    
    Parameters:
    
    es (Elasticsearch): Elasticsearch client.
    
    line (str): Line from the dataset.
    
    i (int): Index or identifier for the line.
    
    df (pd.DataFrame): DataFrame containing FOS information for all documents in the dataset.
    
    Returns: None

    ---------------------------------------

    main()
    
    Purpose: Main function to read the dataset, convert each line to a DataFrame, and initiate BM25 searches for each document.
    
    Parameters: None
    
    Returns: None

    ---------------------------------------




    3) Results_of_eval: Results_of_evaluation:  calculates the average recall and precision metrics based on data stored in the file Data/data_about_good_rec_recall.txt. The file contains information about the quality of recommendations, including recall and precision values for both top-5 and top-10 recommendations.

    main()
    
    Purpose: Main function to execute the entire process of calculating average recall and precision metrics.
    
    Parameters: None
    
    Returns: None.


Python 3.10.9

Versions of the libraries: 

pandas==1.5.3 

elasticsearch==8.11

transformers==4.35.2

chromadb==0.4.18

torch==2.1.1




