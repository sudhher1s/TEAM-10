"""
Complete Flow: Module 1 → Module 2
From Raw Medical Data to Semantic Embeddings
"""

print("\n" + "=" * 100)
print("COMPLETE PIPELINE: MODULE 1 → MODULE 2")
print("=" * 100)

print("""

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            INITIAL STATE: RAW CSV FILES                                 │
└─────────────────────────────────────────────────────────────────────────────────────────┘

Input files:
  • ICD10codes.csv          - 71,704 ICD-10 medical codes (messy, inconsistent)
  • icd9to10dictionary.txt  - 15,086 ICD-9 to ICD-10 mappings
  • cpt.csv, snomed.csv     - CPT and SNOMED codes (optional)

Example raw CSV row:
  Row: [A000, "CHOLERA...", "  vibrio cholerae...  ", "Infectious", "CHOLERA", "cholerae"]
       ↑     ↑                ↑                       ↑              ↑         ↑
    code  short_desc      long_desc(messy)        category      alt_name  variant


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         MODULE 1: DATA & KB BUILDER                                     │
│                    Input: Raw CSV → Output: Clean KB (JSON)                             │
└─────────────────────────────────────────────────────────────────────────────────────────┘

PROCESS (happens in Module 1):
  1. Load Raw Data
     ├─ Read ICD10codes.csv (71,704 rows)
     ├─ Parse each row into dictionary
     └─ Handle missing/malformed entries

  2. Normalize Data
     ├─ Lowercase all text
     ├─ Remove extra whitespace
     ├─ Expand abbreviations (CHF → congestive heart failure)
     ├─ Generate aliases (heart attack, MI, AMI all point to I21.01)
     └─ Validate (check for missing fields)

  3. Deduplicate
     ├─ Find exact duplicates
     ├─ Merge similar entries
     └─ Keep 71,704 unique items

  4. Index & Persist
     ├─ Create code → item mapping (O(1) lookup)
     └─ Save to JSON file: kb.json

OUTPUT OF MODULE 1:
  File: working_modules/module_1_data_kb/output/kb.json
  
  Format: JSON list of 71,704 item objects
  [
    {
      "code": "A000",
      "title": "cholera due to vibrio cholerae 01, biovar cholerae",
      "description": "cholera due to vibrio cholerae 01, biovar cholerae",
      "category": "cholera",
      "code_system": "ICD-10",
      "aliases": ["cholera due"],
      "parent_code": null,
      "metadata": {}
    },
    {
      "code": "A001",
      "title": "cholera due to vibrio cholerae 01, biovar eltor",
      "description": "cholera due to vibrio cholerae 01, biovar eltor",
      "category": "cholera",
      ...
    },
    ... (71,702 more items)
  ]

✓ All items normalized (lowercase, no extra spaces)
✓ Abbreviations expanded to full meaning
✓ Aliases generated for better retrieval
✓ Validated (no missing fields, no duplicates)


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                       MODULE 2: EMBEDDINGS BUILDER                                      │
│              Input: Clean KB (JSON) → Output: Semantic Vectors (NumPy)                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘

PROCESS (happens in Module 2):

  1. Load KB from Module 1
     Input: kb.json (71,704 items)
     ├─ Parse JSON
     ├─ Extract each item's code, title, description
     └─ Validate structure

  2. Prepare Text
     For each item, create concatenated text:
     
     text = title + " " + description
     
     Example:
       Item A000:
         title: "cholera due to vibrio cholerae 01, biovar cholerae"
         description: "cholera due to vibrio cholerae 01, biovar cholerae"
         →
         text: "cholera due to vibrio cholerae 01, biovar cholerae cholera 
                due to vibrio cholerae 01, biovar cholerae"

  3. Initialize Model
     ├─ Load all-MiniLM-L6-v2 from HuggingFace
     ├─ Model: 6-layer transformer (384-dim output)
     └─ Device: CPU (or GPU if available)

  4. Batch Encoding (in batches of 32)
     
     ┌─ Batch 1 (items 0-31)
     │  text_0: "cholera due to vibrio..."
     │  text_1: "cholera due to vibrio..."
     │  ...
     │  text_31: "dengue fever"
     │
     │  [All 32 texts] → [SentenceTransformer.encode()] → [32 vectors of 384-dim]
     │
     │  embedding_0: [0.123, -0.456, 0.789, ..., 0.234]  ← 384 numbers
     │  embedding_1: [0.145, -0.512, 0.654, ..., 0.201]
     │  ...
     │  embedding_31: [0.098, -0.478, 0.721, ..., 0.256]
     │
     └─ Save to embeddings matrix row 0-31

     ┌─ Batch 2 (items 32-63)
     └─ [Continue...]
     
     ... (2,223 total batches for 71,704 items)
     
     Total time: 470.84 seconds (~7.8 minutes on CPU)

  5. Create Metadata & Mappings
     ├─ item_metadata.json: {embeddings_id, code, title, category, description}
     ├─ code_to_index.json: {"A000": 0, "A001": 1, "A009": 2, ...}
     └─ metadata.json: {model_name, embedding_dim, num_embeddings, timestamp}

OUTPUT OF MODULE 2:

  Directory: working_modules/output/
  
  1. embeddings.npy (110 MB)
     NumPy array of shape (71,704, 384)
     
     Row 0 (code A000): [0.123, -0.456, 0.789, ..., 0.234]  ← 384-dim vector
     Row 1 (code A001): [0.145, -0.512, 0.654, ..., 0.201]
     Row 2 (code A009): [0.098, -0.478, 0.721, ..., 0.256]
     ...
     Row 71703 (code Z9989): [0.167, -0.534, 0.687, ..., 0.289]

  2. item_metadata.json (22 MB)
     {
       "embeddings_id": 0,
       "code": "A000",
       "title": "cholera due to vibrio cholerae 01, biovar cholerae",
       "description": "cholera due to vibrio cholerae 01, biovar ch...",
       "category": "cholera",
       "embedding_dim": 384
     },
     {
       "embeddings_id": 1,
       "code": "A001",
       ...
     }

  3. code_to_index.json (1.5 MB)
     {
       "A000": 0,
       "A001": 1,
       "A009": 2,
       "A0100": 3,
       ...
       "Z9989": 71703
     }

  4. metadata.json (190 bytes)
     {
       "model_name": "all-MiniLM-L6-v2",
       "embedding_dim": 384,
       "num_embeddings": 71704,
       "num_kb_items": 71704,
       "timestamp": "2025-12-14T00:07:01.119989",
       "kb_version": "v1.0"
     }

  5. stats.json (281 bytes)
     {
       "total_items": 71704,
       "embedded_items": 71704,
       "failed_items": 0,
       "embedding_time_seconds": 470.84,
       "avg_time_per_item_ms": 6.566,
       "embedding_dim": 384,
       "model_name": "all-MiniLM-L6-v2",
       "timestamp": "2025-12-14T00:07:01.224367"
     }


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         TRANSFORMATION SUMMARY                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘

INPUT (Module 1):
  Raw CSV row:
    "A000,CHOLERA DUE TO VIBRIO CHOLERAE,  vibrio cholerae biovar  ,Infectious"
                                              ↑ messy, inconsistent
OUTPUT (Module 1):
  Clean KB item (JSON):
    {
      "code": "A000",
      "title": "cholera due to vibrio cholerae 01, biovar cholerae",
      "description": "cholera due to vibrio cholerae 01, biovar cholerae",
      "category": "cholera",
      "aliases": ["cholera due"]
    }


INPUT (Module 2):
  Clean KB item (text):
    "cholera due to vibrio cholerae 01, biovar cholerae cholera due to 
     vibrio cholerae 01, biovar cholerae"
                                              ↑ clean, normalized text
OUTPUT (Module 2):
  Semantic vector (384-dimensional):
    [0.123, -0.456, 0.789, ..., 0.234]
         ↑
    Each number represents a learned semantic feature
    E.g., dimension 42 might be "infectious disease severity"
          dimension 157 might be "bacterial origin"
          dimension 284 might be "gastrointestinal impact"


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            WHAT THE EMBEDDINGS MEAN                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘

Each 384-dimensional vector represents the SEMANTIC MEANING of the medical code text.

Similar codes have SIMILAR vectors:
  
  code A000 (cholera): [0.123, -0.456, 0.789, ..., 0.234]
  code A001 (cholera): [0.145, -0.512, 0.654, ..., 0.201]
         
         Cosine similarity = 0.92  ← Very similar! Both are cholera.

  code A000 (cholera):    [0.123, -0.456, 0.789, ..., 0.234]
  code I21.01 (MI):       [0.567, 0.234, -0.123, ..., 0.789]
         
         Cosine similarity = 0.15  ← Very different! Different organ systems.

This is why Module 2 is crucial: it converts medical text into a numerical 
space where SEMANTIC SIMILARITY = GEOMETRIC PROXIMITY.


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          NEXT: MODULE 3 & BEYOND                                        │
└─────────────────────────────────────────────────────────────────────────────────────────┘

Module 3 (Vector Index - NEXT):
  Input: embeddings.npy (71,704 × 384)
  Process: Build FAISS ANN index for fast nearest-neighbor search
  Output: FAISS index file (enables <5ms similarity search)
  
Module 4 (Query Encoder):
  Input: User query (text)
  Process: Use same all-MiniLM-L6-v2 to encode query to 384-dim vector
  Output: Query embedding (can now be compared to KB embeddings)
  
Module 5 (Cross-Encoder Reranker):
  Input: Top-K candidates from Module 3, user query
  Process: Use cross-encoder to score each candidate pair-wise
  Output: Re-ranked top-K results with confidence scores

RAG Pipeline (Modules 6-10):
  6. Evidence Extraction: Extract relevant passages for each code
  7. Guardrails/Policy: Apply compliance rules (no hallucinations)
  8. LLM Chatbot: Ground LLM responses with retrieved medical codes
  9. Orchestrator: Wire all modules together
  10. Evaluation & Serving: Test accuracy, deploy API

""")

print("\n" + "=" * 100)
print("KEY INSIGHT:")
print("=" * 100)
print("""
Module 1: TEXT QUALITY
  "Messy raw data" → "Clean, normalized, validated KB"
  
Module 2: NUMERICAL REPRESENTATION
  "Clean KB text" → "384-dimensional semantic vectors"
  
Together: Enable AI-powered medical code retrieval
  Query: "heart attack"
  → Encode to vector
  → Find similar vectors in embedding space
  → Return codes like I21.01, I21.02 (myocardial infarction variants)
  
This is the core of Retrieval-Augmented Generation (RAG) for medical coding!
""")
