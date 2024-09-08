# Scholarly Hybrid QA ISWC 2024


## Overview

The Scholarly Hybrid QA project addresses the Scholarly Hybrid Question Answering over Linked Data (QALD) Challenge at the International Semantic Web Conference (ISWC) 2024. This challenge involves developing Question Answering (QA) systems that integrate and query information from diverse scholarly data sources: DBLP Knowledge Graph, SemOpenAlex Knowledge Graph, and Wikipedia-based texts.

Our approach combines SPARQL queries, divide and conquer algorithms, and BERT-based predictions to handle complex queries and provide accurate responses.

## Table of Contents

- [Introduction](#introduction)
- [Methodology](#methodology)
- [Installation](#installation)
- [Usage](#usage)
- [Results](#results)

## Introduction

The Scholarly Hybrid QA project aims to answer questions related to scholarly publications using a combination of SPARQL queries and large language models (LLMs). The main components of our system include:

1. **DBLP Knowledge Graph**: A dataset of research publications, authors, and affiliations.
2. **SemOpenAlex Knowledge Graph**: A comprehensive KG with information about authors, institutions, and publications.
3. **Wikipedia-Based Scholarly Text**: Textual data from Wikipedia related to scholarly topics.

## Methodology

Our approach involves the following steps:

1. **Data Processing and Query Execution**:
   - Execute SPARQL queries against SemOpenAlex to gather data.
   - Clean and organize the data for further processing.

2. **Divide and Conquer Approach**:
   - Segment and classify questions based on their content and identifiers.
   - Implement a divide and conquer strategy to handle various question types.

3. **Data Retrieval and Aggregation**:
   - Generate and process CSV files with potential responses.
   - Convert CSV to JSON, merge results, and refine answers.

4. **Large Language Model-Based Predictions**:
   - Utilize BERT-base-cased-squad2 for predicting responses to personal author questions.
   - Integrate LLM-generated responses with SPARQL query results.

5. **Evaluation**:
   - Submit results to Codalab and evaluate using Exact Match and F-score metrics.

## Installation

1. Clone the repository:

    ```bash
    mkdir schorlaly-qa-2024
    cd schorlaly-qa-2024
    git clone https://github.com/FOMUBAD-BORISTA-FONDI/Scholarly-Hybrid-QA-ISWC-2024.git
   ```
## Access an run it.

### Getting started

#### Setup environment

2. Create a virtual environment and install the requirements:

    ```bash
    conda create -n schorlaly-qa-2024 python=3.12.1
    ```

    ```bash
    conda activate schorlaly-qa-2024
    ```

1. Navigate to the project directory:

    ```bash
    cd Scholarly-Hybrid-QA-ISWC-2024
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

# Usage

## PIPELINE 1

1. Prepare your SPARQL query files and input datasets.

2. Access the prediction-3 folder

3. Run the first-script to predict locally:

    ```bash
    python local-predict.py
    ```
4. The answers would be predicted and saved in a file named `prediction-3.json`.
    #### Note that: 
    ##### 3.1 This prediction takes about 60-70hours to predicted about 334 questions dataset.
    ##### 3.2 I ran it already and save a version.
    ##### 3.3 You can use this, in-case of time constraints
 
## PIPELINE 2 

3. Execute the divide and conquer approach:

    ```bash
    Access the prediction 2 folder and run each the script respectively to segment the given dataset.
    ```
    1. Access the remove_list_uri folder, run the command
    ```bash
    python remove_list_uri.py
    ```
    2. Access the Authors vs institution-break folder, run the command
    ```bash
    python divide-author-institution-data.py
    ```
    3. Access the `Authors vs institutions-break/authors/2YearsMeanCitedness` folder, run the command
    ```bash 
    python 2yearsmean.py
    ```
    4. Do same for the rest by accessing each of the broken-down folders and running their correspoding script, Do this by running the command
    ```bash
    python _filename_.py
    ```
    5. Now move to the Institution folder and do same thing as the author folder.  Access the `Authors vs institutions-break/institution/acronym` folder, run the command
    ```bash
    python acronym.py
    ```
    6. Do same for the rest by accessing each of the broken-down folders and running their correspoding script, Do this by running the command
    ```bash
    python _filename_.py
    ```
    7. Now run `Prediction-2/algo_test_fine.py` to do the final predictions. But note that, this is done after adding the key field.
    ```bash
    python algo_test_fine
    ```
## PIPELINE 3

0. Generate predictions using the LLM:

1. Prepare files and input datasets.

2. Access the prediction-1 folder

3. Run the script to extract-context for each given question:
    Access the Extract context folder;

    ```bash
    python extract_context.py
    ```
    This would extract the context for each question and save it in the "processed_questions..." folder

    #### Note that: 
    ##### 3.1 The extraction of the context takes about 3-4hours to complete all 702 questions dataset.
    ###### 3.1.1 Here is how it works, A general extraction for each question is done, and where it does not find any context, it leaves it blank. About 400 questions had a context. Now a second file is ran, this file is to get the wikipedia page content of each author. This would be used to refine the context.
    ##### 3.2 I ran them, refined them already and saved a version of it in the stated location.
    ##### 3.3 You can use this, in-case of time constraints.

4. Run the script to predict answers:

    ```bash
    python llm_bert.py
    ```
     The answers would be predicted and saved in a folder named `save-prediction`.
    
    #### Note that: 
    ##### 4.1 This prediction takes about 3-4hours to predicted about 683 questions dataset.
    ###### 4.1.1 Here is how it works, Its does a general prediction for questions with context, and where it does not find an answer, the llm predicts and answer.
    ##### 4.2 I ran it already and save a version of it in the stated location.
    ##### 4.3 You can use this, in-case of time constraints.

## Refinement

1. Prepare your outputed result files.

2. Access the Refinement folder

3. Run the command:

    ```bash
    python refineanswers2.py
    ```
    This would refine the `answers2.txt` file and save it. This can  then be submitted to `codalab` for evaluation.

## Submision

1. Submit the results:

    ```bash
    Accees the Codalab platform and submit the results.
    ```

## Results

Our approach demonstrated significant improvements in handling complex queries and providing accurate responses. For detailed results and performance metrics, consult the article for in-depth analysis.

Here are some metrics for the results:



