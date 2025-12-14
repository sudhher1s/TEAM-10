# Architecture Overview of the Healthcare Medical Coding Assistant

## Introduction
The Healthcare Medical Coding Assistant is designed to streamline the process of medical coding by utilizing advanced algorithms and machine learning techniques. This project aims to assist healthcare professionals in accurately mapping clinical notes to appropriate medical codes, ensuring compliance with healthcare regulations.

## System Architecture
The system is structured into several key components, each responsible for specific functionalities:

### 1. **Frontend**
- **User Interface**: A web-based interface where healthcare professionals can input clinical notes and receive coding suggestions.
- **API Integration**: Communicates with the backend services to fetch coding predictions and other relevant data.

### 2. **Backend**
- **API Layer**: Built using FastAPI, this layer handles incoming requests and routes them to the appropriate services.
  - **Routes**:
    - **Coding**: Handles requests related to medical coding predictions.
    - **Audit**: Logs requests and responses for auditing purposes.
    - **Health**: Provides a health check endpoint to ensure the service is operational.
- **Middleware**: Implements authentication and validation to secure the API and ensure data integrity.

### 3. **Services**
- **Coding Engine**: The core logic that maps clinical notes to ICD-10 codes using machine learning models.
- **Terminology Service**: Manages terminology-related functions, including fetching descriptions and categories for codes.
- **Compliance Service**: Ensures that all operations adhere to healthcare regulations and guidelines.
- **LLM Integration**: Incorporates a language model for advanced processing and reranking of coding suggestions.

### 4. **Data Processing Pipelines**
- **Preprocessing**: Prepares clinical notes for input into the coding engine, including text normalization and feature extraction.
- **Postprocessing**: Formats the output from the coding engine for API responses, ensuring clarity and usability.
- **Mapping**: Contains functions for converting ICD-9 codes to ICD-10 codes, facilitating backward compatibility.

### 5. **Data Storage**
- **Raw Data**: Stores raw claims, encounters, and clinical notes for processing.
- **Reference Data**: Contains reference datasets for ICD-10, CPT, and SNOMED codes.
- **Processed Data**: Holds training and evaluation datasets in a format suitable for model training.

### 6. **Testing**
- Comprehensive unit tests are implemented for the API routes, services, and data processing pipelines to ensure reliability and correctness.

## Technologies Used
- **FastAPI**: For building the API layer.
- **TypeScript**: For type safety and better development experience.
- **Machine Learning**: For coding predictions and data processing.
- **PostgreSQL**: For data storage (if applicable).

## Conclusion
The Healthcare Medical Coding Assistant is a robust system designed to enhance the efficiency and accuracy of medical coding. By leveraging modern technologies and methodologies, it aims to support healthcare professionals in their coding tasks while ensuring compliance with industry standards.