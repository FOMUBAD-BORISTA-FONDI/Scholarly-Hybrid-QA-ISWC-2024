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
- [Contributing](#contributing)
- [License](#license)

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
   git clone https://github.com/yourusername/scholarly-hybrid-qa-iswc-2024.git
## Installation

1. Navigate to the project directory:

    ```bash
    cd scholarly-hybrid-qa-iswc-2024
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Prepare your SPARQL query files and input datasets.

2. Run the first-script to predict locally:

    ```bash
    python local-predict.py
    ```

3. Execute the divide and conquer approach:

    ```bash
    Access the prediction 2 file and run the scripts to segment the dataset.
    ```

4. Generate predictions using the LLM:

    ```bash
    python llm_pert.py file to getresults 
    ```

5. Submit the results:

    ```bash
    Accees the Codalab platform and submit the results.
    ```


# THIS IS A DRAFT README FILE TO RESPECT THE DATELINE. THE REAL READMe.md FILE WOULD BE UPLOADED SOON!!!
## Results

Our approach demonstrated significant improvements in handling complex queries and providing accurate responses. For detailed results and performance metrics, refer to the `results` directory or consult the article for in-depth analysis.

