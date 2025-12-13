# 🏥 AI‑Powered Medical Coding & Doctor‑Assist Agent

> **A human‑centric, agent‑driven healthcare AI system for clinical documentation, ICD‑10 coding, and doctor assistance**

---

## 🔴 Problem Statement

Modern healthcare systems generate massive amounts of **unstructured clinical data** — patient voice conversations, handwritten or free‑text notes, and discharge summaries. Converting this data into **structured medical records and ICD‑10 codes** is a critical but painful process.

### Current challenges:

* Manual medical coding is **slow and expensive**
* High chance of **coding errors**, impacting insurance claims
* Doctors spend more time **documenting than treating** patients
* Existing systems lack **explainability and trust**
* Voice-based patient intake is still poorly utilized

As a result, healthcare providers face **burnout, delayed reimbursements, and reduced care quality**.

---

## 🟢 Proposed Solution

We present an **Agent‑Driven AI Medical Assistant** that acts as a **clinical co‑pilot** for doctors.

The system:

* Listens to patient complaints (voice or text)
* Converts speech into clinical notes
* Analyzes sentiment and urgency
* Extracts symptoms and medical entities
* Maps notes to **ICD‑10 codes** using hybrid retrieval (BM25 + embeddings)
* Generates **doctor‑editable prescription drafts**
* Enforces strict **medical guardrails and human‑in‑the‑loop approval**

At the heart of the system is an **AI Agent** that plans, reasons, calls tools, and ensures safety.

> ⚠️ The system is **assistive, not autonomous**. Final decisions always remain with licensed doctors.

---

## 🎯 Expected Outcomes

* ⏱️ Faster ICD‑10 coding and documentation
* 📉 Reduced administrative burden for doctors
* 🧾 Improved insurance claim accuracy
* 🧠 Explainable AI decisions with evidence
* 🎙️ Voice‑enabled, patient‑friendly intake

---

## 🧠 AI Agent – Detailed Explanation (Core of the System)

The **AI Agent** is the most critical component of this project. Instead of building a fixed, hard‑coded pipeline, we designed an **intelligent, goal‑driven agent** that controls and coordinates all modules.

This makes the system flexible, explainable, and safe for healthcare use.

---

### 🤖 What Exactly the Agent Does

The agent acts like a **clinical workflow coordinator**, similar to a junior medical assistant working under a doctor.

It performs the following responsibilities:

* Understands the **overall goal** (assist documentation & coding)
* Breaks the task into **logical steps**
* Decides **which tool/module to call next**
* Validates intermediate outputs
* Applies **confidence checks and guardrails**
* Escalates to a human doctor when required

---

### 🧩 Agent Capabilities

The agent is designed with the following capabilities:

* **Planning:** Decides the execution order of modules
* **Tool Usage:** Calls ASR, NER, retrieval, reranker, and LLM tools
* **Memory:** Maintains context across steps (patient symptoms, urgency)
* **Reasoning:** Evaluates if outputs are confident or ambiguous
* **Safety Control:** Blocks unsafe or uncertain medical actions

---

### 🛠️ Tools Used by the Agent

The agent interacts with multiple tools, including:

* Speech-to-Text tool (Whisper)
* Sentiment & urgency analyzer
* Symptom/entity extraction model
* ICD‑10 retrieval engine (BM25 + embeddings)
* Reranking model
* Prescription draft generator (LLM)

The agent **does not generate medical decisions blindly** — it uses tools and validates results step by step.

---

### 🧠 Agent Decision Flow (Simplified)

1. Receive patient input (voice/text)
2. Decide whether speech-to-text is needed
3. Run sentiment & urgency detection
4. If emergency → escalate immediately
5. Extract symptoms and entities
6. Trigger ICD‑10 retrieval
7. Rerank and verify confidence
8. Generate prescription draft (assistive)
9. Send output for doctor review

---

### 🛡️ Agent Guardrails & Safety Logic

The agent enforces strict safety rules:

* No autonomous diagnosis
* No final prescriptions
* Mandatory doctor review
* Emergency keywords override automation
* Low confidence → human escalation

This ensures the agent behaves responsibly in a sensitive healthcare environment.

---

### 🧪 Why an Agent-Based Design?

Using an agent instead of a fixed pipeline provides:

* Better handling of **real‑world variability**
* Improved explainability
* Easier future expansion
* Strong alignment with **responsible AI principles**

---

## 🏗️ System Design (High‑Level Architecture)

```
Patient Voice / Text
        ↓
Speech‑to‑Text (Whisper)
        ↓
Sentiment & Urgency Detection
        ↓
Symptom & Entity Extraction
        ↓
AI Agent (Planner & Controller)
        ↓
ICD‑10 Retrieval (BM25 + Embeddings)
        ↓
Reranking & Explainability
        ↓
Prescription Draft Generator
        ↓
Doctor Review & Approval
```

---

## 🔗 Data Links

### Primary Dataset

* **MIMIC‑III Clinical Notes** (de‑identified, open access)
* Link: [https://physionet.org/content/mimiciii/1.4/](https://physionet.org/content/mimiciii/1.4/)

> Access requires quick registration on PhysioNet.

### Medical Standards

* **ICD‑10 Code Dataset** (WHO / CMS public releases)

---

## 📊 Data Used

* De‑identified clinical notes (discharge summaries, progress notes)
* Synthetic patient voice inputs for demo
* ICD‑10 descriptions and hierarchies

No personal or identifiable patient data is used.

---

## 🧩 Key Assumptions

* The system assists **trained medical professionals only**
* Clinical notes are reasonably descriptive
* Doctors will review and approve outputs
* ICD‑10 mapping is probabilistic, not deterministic
* Emergency detection must always override automation

---

## 🔄 10‑Phase Workflow (End‑to‑End)

### 1️⃣ Guardrails & Ethics Setup

Define medical boundaries, disclaimers, and emergency escalation rules.

### 2️⃣ Agent Architecture Design

Create a tool‑using planner agent with memory and decision logic.

### 3️⃣ Speech‑to‑Text

Convert patient voice into structured clinical text.

### 4️⃣ Sentiment & Urgency Analysis

Detect pain, anxiety, or emergency conditions.

### 5️⃣ Symptom & Entity Extraction

Extract symptoms, duration, severity, and clinical entities.

### 6️⃣ ICD‑10 Retrieval (H10 Core)

Hybrid retrieval using BM25 and vector embeddings.

### 7️⃣ Reranking & Explainability

Improve ranking and highlight justification spans.

### 8️⃣ Prescription Draft Generation

Generate a structured, doctor‑editable draft.

### 9️⃣ Doctor Review & Approval

Human‑in‑the‑loop validation.

### 🔟 UI, Deployment & Evaluation

Polish UI, deploy services, and measure accuracy.

---

## 📥 Inputs & 📤 Outputs

### Inputs

* Patient voice or text
* Clinical notes
* ICD‑10 reference data

### Outputs

* Transcribed clinical notes
* Sentiment & urgency scores
* Extracted symptoms
* Ranked ICD‑10 codes with explanations
* Doctor‑approved prescription draft

---

## 🧰 Tech Stack Used

### Frontend

* Next.js (React)
* Tailwind CSS
* Framer Motion (animations)
* shadcn/ui

### Backend

* Python
* FastAPI
* LangChain (Agent framework)

### AI / ML

* Whisper (ASR)
* scispaCy / BioBERT (NER)
* Sentence‑Transformers (Embeddings)
* BM25 + FAISS (Retrieval)
* Cross‑Encoder (Reranking)

### Data

* MIMIC‑III
* ICD‑10 datasets

---

## 🧩 Applications & Use Cases

* Hospitals and clinics
* Medical coding teams
* Telemedicine platforms
* Insurance claim processing
* Clinical documentation automation

---

## 🌟 Advantages & Impact

### Advantages

* Explainable and trustworthy AI
* Reduced manual effort
* Voice‑first clinical intake
* Modular and scalable design

### Impact

* Reduced doctor burnout
* Faster reimbursements
* Improved patient experience
* Safer adoption of GenAI in healthcare

---

## 🛡️ Ethics, Safety & Compliance

* Assistive AI only
* No autonomous diagnosis
* Doctor always in control
* Emergency escalation enabled
* Uses only de‑identified data

---



