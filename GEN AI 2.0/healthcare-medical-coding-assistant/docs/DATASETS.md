# Datasets Used in the Healthcare Medical Coding Assistant

This document provides an overview of the datasets utilized in the Healthcare Medical Coding Assistant project. The datasets are categorized into raw, reference, and processed data.

## 1. Raw Datasets

These datasets contain unprocessed data that will be used for training and evaluation purposes.

- **claims.csv**: This file includes raw claims data, which contains information about healthcare services provided to patients, including diagnosis and treatment codes.
  
- **encounters.csv**: This file contains raw encounter data, detailing patient visits to healthcare providers, including timestamps and associated medical codes.
  
- **notes.jsonl**: This file consists of raw clinical notes in JSON Lines format, capturing detailed narratives from healthcare providers regarding patient care.

## 2. Reference Datasets

These datasets provide standard coding references that are essential for mapping and coding medical information.

- **icd10cm.csv**: This file contains reference data for ICD-10-CM (International Classification of Diseases, 10th Revision, Clinical Modification) codes, which are used for diagnosis coding.
  
- **cpt.csv**: This file includes reference data for CPT (Current Procedural Terminology) codes, which are used to describe medical, surgical, and diagnostic services.
  
- **snomed.csv**: This file contains reference data for SNOMED CT (Systematized Nomenclature of Medicine Clinical Terms), a comprehensive clinical terminology used for electronic health records.

## 3. Processed Datasets

These datasets have been processed and formatted for training and evaluation of the machine learning models.

- **training.tsv**: This file contains processed training data in TSV (Tab-Separated Values) format, structured for input into the model.
  
- **evaluation.tsv**: This file includes processed evaluation data in TSV format, used to assess the performance of the trained model.

## Conclusion

The datasets outlined in this document are crucial for the development and functionality of the Healthcare Medical Coding Assistant. They enable the application to accurately map clinical notes to appropriate medical codes, ensuring compliance and improving healthcare documentation efficiency.