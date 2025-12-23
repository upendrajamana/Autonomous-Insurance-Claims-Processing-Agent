# Autonomous Insurance Claims Processing Agent

## Project Description

This project implements a lightweight Python-based agent to automate the **initial processing of insurance FNOL (First Notice of Loss) documents**.

The system reads FNOL documents, extracts key claim details, checks for missing or suspicious information, and routes the claim to the appropriate workflow based on predefined business rules.

---

## Features

* Supports FNOL documents in **TXT and PDF** format
* Extracts important claim-related fields
* Identifies missing mandatory information
* Detects suspicious keywords in claim descriptions
* Automatically routes claims to the correct processing queue
* Outputs results in structured **JSON format**

---

## Extracted Fields

* Policy Number
* Policyholder Name
* Incident Date
* Incident Location
* Incident Description
* Claim Type
* Estimated Damage

---

## Claim Routing Rules

| Condition                       | Routing Decision |
| ------------------------------- | ---------------- |
| Mandatory fields missing        | Manual Review    |
| Fraud-related keywords detected | Investigation    |
| Claim type involves injury      | Specialist Queue |
| Estimated damage < 25,000       | Fast-track       |
| Otherwise                       | Standard Review  |

Each routing decision includes a brief reasoning message.

---

## Output Format

```json
{
  "extractedFields": {},
  "missingFields": [],
  "recommendedRoute": "",
  "reasoning": ""
}
```

---

## How to Run

### 1. Install dependencies

```bash
pip install pdfplumber
```

### 2. Run the application

```bash
python app.py <path_to_fnol_file>
```

Example:

```bash
python app.py samples/fnol_sample_1.txt
```

---

## Output

* Results are printed to the console
* A JSON output file is saved automatically in the same directory

---

## Project Structure

```
project/
│── app.py
│── README.md
│── samples/
│   └── fnol_sample_1.txt
```

---

## Technologies Used

* Python
* Regular Expressions
* pdfplumber

---

## Notes

* This system performs **initial claim triage only**
* Final claim approval or rejection is handled outside this scope
* Logic is rule-based for clarity and explainability

---

**Author:** Upendra
**Purpose:** Technical Assessment
**Language:** Python
