# DB MCP (HR CSV → SQLite) — Open Source Reference

This folder contains a **fully open-source** Model Context Protocol (MCP) server implementation that:

- Loads an HR “people” CSV file
- Reads **3 lines of metadata** at the top of the CSV (comment lines starting with `#`)
- Imports the CSV into an **in-memory SQLite** database
- Exposes **read-only MCP tools** over **stdio** (newline-delimited JSON-RPC 2.0)

No Claude Desktop setup is required. A small Python client is included for testing.

## Files

- `db_mcp_server.py` — MCP server (stdio)
- `db_mcp_client.py` — simple MCP stdio client for testing
- `data/hr_people.csv` — sample HR CSV with 3-line metadata header

## Run the server

```bash
python db_mcp_server.py
```

Optionally pass a custom CSV path:

```bash
python db_mcp_server.py /path/to/your/hr_people.csv
```

Or set an environment variable:

```bash
HR_CSV_PATH=/path/to/your/hr_people.csv python db_mcp_server.py
```

## Test with the included client (recommended)

```bash
python db_mcp_client.py
```

You should see:

- `initialize` handshake
- `tools/list`
- a sample SQL query result
- an interactive prompt to run more `SELECT` queries

## Tools exposed

- `hr_metadata` — returns the 3-line metadata header as a JSON object
- `hr_schema` — returns the SQLite schema for table `employees`
- `hr_query` — execute **read-only** `SELECT`/`WITH` SQL queries
- `hr_find_people` — structured search without writing SQL

## CSV metadata format (first 3 lines)

Example:

```text
# dataset: HR People
# description: Synthetic employee roster for MCP demo (no real PII)
# primary_key: employee_id
employee_id,first_name,last_name,...
```

Metadata lines are parsed as `key: value`. If a line is not `key: value`, it is stored as `meta_line_1`, `meta_line_2`, etc.

## Notes for sharing

- Everything here is standard-library Python (SQLite + CSV).
- The demo data is synthetic (no real PII).
- The server writes **only JSON-RPC** to stdout. Logs go to stderr (safe for stdio MCP).

##How to run
# Server (auto-builds index if missing)
python mcp_server.py

# Test client
python client.py (interactive mode)

python client.py --search "diabetes treatment" --top-k 5   

#add more documentation files:

    Drop .txt or .md files into ./docs/

Rebuild:

python build_doc_index.py --docs_dir ./docs --out_map ./doc_map.json --out_db ./doc_i

#run sample
```
--terminal 1
 C:\Users\davidzhang\Downloads\ml\ml\doc_mcp_1>python mcp_server.py
[doc_mcp_server] Loaded 1 docs. FTS5=yes
[doc_mcp_server] Ready.


--terminal 2
 C:\Users\davidzhang\Downloads\ml\ml\doc_mcp_1>python client.py --search "diabetes treatment" --top-k 5
[doc_mcp_server] Loaded 1 docs. FTS5=yes
[doc_mcp_server] Ready.
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"query\": \"diabetes treatment\",\n  \"top_k\": 5,\n  \"matches\": [\n    {\n      \"doc_id\": \"cdc-diabetes-treatment-guidelines\",\n      \"title\": \"CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\",\n      \"chunk_id\": 3,\n      \"score\": 3.3014800093648174e-06,\n      \"snippet\": \"…Type 2 [diabetes] with circulatory complications\\n- I50.9: Heart failure (if present)\\n\\n### 3.2 Aggressive [Treatment]…\",\n      \"text\": \"itoring (CGM)\\n- Kidney function testing: Every 6 months\\n- Eye examination: Every 6-12 months\\n\\n### 2.5 Enhanced Interventions\\n- Referral to certified diabetes care and education specialist\\n- Quarterly nutritionist consultations\\n- Structured exercise program\\n- Cardiovascular risk assessment\\n- Sleep apnea screening if indicated\\n- Depression and diabetes distress screening\\n\\n### 2.6 Complication Screening\\nBiannual assessments:\\n- Comprehensive foot examination\\n- Monofilament testing for neuropathy\\n- Ankle-brachial index if claudication symptoms\\n- Retinal photography or dilated eye exam\\n\\n---\\n\\n## Section 3: HIGH RISK PATIENTS (60-80% Complication Probability)\\n\\n### 3.1 ICD-10-CM Coding\\nPrimary codes:\\n- E11.65: Type 2 diabetes with hyperglycemia\\n- E11.69: Type 2 diabetes with other specified complication\\n- E11.8: Type 2 diabetes with unspecified complications\\n\\nComplication-specific codes as identified:\\n- E11.21: Type 2 diabetes with diabetic nephropathy\\n- E11.311-319: Type 2 diabetes with diabetic retinopathy\\n- E11.40-49: Type 2 diabetes with diabetic neuropathy\\n- E11.51-59: Type 2 diabetes with circulatory complications\\n- I50.9: Heart failure (if present)\\n\\n### 3.2 Aggressive Treatment Goals\"\n    },\n    {\n      \"doc_id\": \"cdc-diabetes-treatment-guidelines\",\n      \"title\": \"CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\",\n      \"chunk_id\": 15,\n      \"score\": 3.258944413339537e-06,\n      \"snippet\": \"ational [Diabetes] Statistics Report (2023)\\n- Endocrine Society Clinical Practice Guidelines\\n- AACE/ACE Comprehensive Type 2 [Diabetes]…\",\n      \"text\": \"ational Diabetes Statistics Report (2023)\\n- Endocrine Society Clinical Practice Guidelines\\n- AACE/ACE Comprehensive Type 2 Diabetes Management Algorithm\\n- AHA/ACC Guideline on the Primary Prevention of Cardiovascular Disease\\n- KDIGO Clinical Practice Guideline for Diabetes Management in CKD\\n- ICD-10-CM Official Guidelines for Coding and Reporting (2024)\\n\\nLast Updated: January 2026\"\n    },\n    {\n      \"doc_id\": \"cdc-diabetes-treatment-guidelines\",\n      \"title\": \"CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\",\n      \"chunk_id\": 14,\n      \"score\": 3.2282155449534986e-06,\n      \"snippet\": \"…This [treatment] protocol is based on:\\n- American [Diabetes] Association Standards of Care in [Diabetes] (2024)\\n- CDC…\",\n      \"text\": \" pain, confusion)\\n- Severe hypoglycemia requiring assistance\\n- Acute complications (MI, stroke, foot infection)\\n- Inability to care for self safely\\n\\n### 4.11 Medication Assistance and Resources\\n\\nFinancial support:\\n- Pharmaceutical patient assistance programs\\n- 340B drug pricing if eligible\\n- Manufacturer coupons and savings cards\\n- State medication assistance programs\\n- Community health center referral if uninsured\\n\\nEquipment and supplies:\\n- CGM coverage verification and prior authorization assistance\\n- Insulin pump coverage if indicated\\n- Blood glucose meter and strip coverage\\n- Sharps disposal containers\\n- Diabetic shoe program (Medicare Part B)\\n\\nCommunity resources:\\n- Transportation services (medical appointments)\\n- Meal delivery programs\\n- Home health aide services\\n- Diabetes education programs\\n- Exercise programs for seniors/disabled\\n\\n---\\n\\n## References and Guidelines\\n\\nThis treatment protocol is based on:\\n- American Diabetes Association Standards of Care in Diabetes (2024)\\n- CDC National Diabetes Statistics Report (2023)\\n- Endocrine Society Clinical Practice Guidelines\\n- AACE/ACE Comprehensive Type 2 Diabetes Management Algorithm\\n- AHA/ACC Guideline on the Primary Prevention o\"\n    },\n    {\n      \"doc_id\": \"cdc-diabetes-treatment-guidelines\",\n      \"title\": \"CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\",\n      \"chunk_id\": 0,\n      \"score\": 3.162101192394457e-06,\n      \"snippet\": \"# CDC [DIABETES] COMPLICATION RISK MANAGEMENT GUIDELINES\\nEvidence-Based [Treatment] Protocols\\n\\n## Section 1: LOW RISK PATIENTS (0…\",\n      \"text\": \"# CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\\nEvidence-Based Treatment Protocols\\n\\n## Section 1: LOW RISK PATIENTS (0-30% Complication Probability)\\n\\n### 1.1 ICD-10-CM Coding\\n- E11.9: Type 2 diabetes mellitus without complications\\n- Z79.4: Long-term (current) use of insulin (if applicable)\\n- E11.00: Type 2 diabetes with hyperosmolarity without coma (if applicable)\\n\\n### 1.2 Treatment Goals\\n- HbA1c target: <7.0% (individualized based on patient factors)\\n- Fasting plasma glucose: 80-130 mg/dL\\n- Postprandial glucose: <180 mg/dL\\n- Blood pressure: <140/90 mmHg\\n- LDL cholesterol: <100 mg/dL\\n\\n### 1.3 Medication Management\\nFirst-line therapy:\\n- Metformin 500-2000 mg daily (if eGFR >30 mL/min)\\n- Lifestyle modifications as foundation\\n\\nAdditional agents if needed:\\n- GLP-1 receptor agonist for cardiovascular benefit\\n- SGLT2 inhibitor for renal and cardiac protection\\n- DPP-4 inhibitor as alternative\\n\\n### 1.4 Monitoring Schedule\\n- Clinic visits: Every 3-6 months\\n- HbA1c testing: Every 6 months if stable, every 3 months if not at goal\\n- Self-monitoring blood glucose: As clinically indicated\\n- Annual comprehensive metabolic panel\\n- Annual lipid panel\\n\\n### 1.5 Preventive Screening\\nAnnual scre\"\n    },\n    {\n      \"doc_id\": \"cdc-diabetes-treatment-guidelines\",\n      \"title\": \"CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\",\n      \"chunk_id\": 1,\n      \"score\": 3.1004835799350414e-06,\n      \"snippet\": \"…Type 2 [diabetes] with chronic kidney disease (if applicable)\\n\\n### 2.2 Enhanced [Treatment] Goals\\n- HbA1c target…\",\n      \"text\": \" if stable, every 3 months if not at goal\\n- Self-monitoring blood glucose: As clinically indicated\\n- Annual comprehensive metabolic panel\\n- Annual lipid panel\\n\\n### 1.5 Preventive Screening\\nAnnual screenings required:\\n- Dilated comprehensive eye examination\\n- Urine albumin-to-creatinine ratio\\n- Serum creatinine and estimated GFR\\n- Comprehensive foot examination\\n- Dental examination\\n\\n### 1.6 Patient Education\\n- Diabetes self-management education (DSME)\\n- Medical nutrition therapy\\n- Physical activity counseling (150 min/week moderate intensity)\\n- Recognition of hypoglycemia and hyperglycemia\\n- Sick-day management\\n- Foot care education\\n\\n### 1.7 Vaccinations\\n- Influenza vaccine annually\\n- Pneumococcal vaccine per CDC guidelines\\n- COVID-19 vaccination and boosters\\n- Hepatitis B vaccine for adults <60 years\\n\\n---\\n\\n## Section 2: MODERATE RISK PATIENTS (30-60% Complication Probability)\\n\\n### 2.1 ICD-10-CM Coding\\n- E11.65: Type 2 diabetes mellitus with hyperglycemia\\n- E11.9: Type 2 diabetes mellitus without complications\\n- Z79.4: Long-term (current) use of insulin\\n- E11.22: Type 2 diabetes with chronic kidney disease (if applicable)\\n\\n### 2.2 Enhanced Treatment Goals\\n- HbA1c target: <7.0% (cons\"\n    }\n  ]\n}"
      }
    ],
    "structuredContent": {
      "query": "diabetes treatment",
      "top_k": 5,
      "matches": [
        {
          "doc_id": "cdc-diabetes-treatment-guidelines",
          "title": "CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES",
          "chunk_id": 3,
          "score": 3.3014800093648174e-06,
          "snippet": "…Type 2 [diabetes] with circulatory complications\n- I50.9: Heart failure (if present)\n\n### 3.2 Aggressive [Treatment]…",
          "text": "itoring (CGM)\n- Kidney function testing: Every 6 months\n- Eye examination: Every 6-12 months\n\n### 2.5 Enhanced Interventions\n- Referral to certified diabetes care and education specialist\n- Quarterly nutritionist consultations\n- Structured exercise program\n- Cardiovascular risk assessment\n- Sleep apnea screening if indicated\n- Depression and diabetes distress screening\n\n### 2.6 Complication Screening\nBiannual assessments:\n- Comprehensive foot examination\n- Monofilament testing for neuropathy\n- Ankle-brachial index if claudication symptoms\n- Retinal photography or dilated eye exam\n\n---\n\n## Section 3: HIGH RISK PATIENTS (60-80% Complication Probability)\n\n### 3.1 ICD-10-CM Coding\nPrimary codes:\n- E11.65: Type 2 diabetes with hyperglycemia\n- E11.69: Type 2 diabetes with other specified complication\n- E11.8: Type 2 diabetes with unspecified complications\n\nComplication-specific codes as identified:\n- E11.21: Type 2 diabetes with diabetic nephropathy\n- E11.311-319: Type 2 diabetes with diabetic retinopathy\n- E11.40-49: Type 2 diabetes with diabetic neuropathy\n- E11.51-59: Type 2 diabetes with circulatory complications\n- I50.9: Heart failure (if present)\n\n### 3.2 Aggressive Treatment Goals"
        },
        {
          "doc_id": "cdc-diabetes-treatment-guidelines",
          "title": "CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES",
          "chunk_id": 15,
          "score": 3.258944413339537e-06,
          "snippet": "ational [Diabetes] Statistics Report (2023)\n- Endocrine Society Clinical Practice Guidelines\n- AACE/ACE Comprehensive Type 2 [Diabetes]…",
          "text": "ational Diabetes Statistics Report (2023)\n- Endocrine Society Clinical Practice Guidelines\n- AACE/ACE Comprehensive Type 2 Diabetes Management Algorithm\n- AHA/ACC Guideline on the Primary Prevention of Cardiovascular Disease\n- KDIGO Clinical Practice Guideline for Diabetes Management in CKD\n- ICD-10-CM Official Guidelines for Coding and Reporting (2024)\n\nLast Updated: January 2026"
        },
        {
          "doc_id": "cdc-diabetes-treatment-guidelines",
          "title": "CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES",
          "chunk_id": 14,
          "score": 3.2282155449534986e-06,
          "snippet": "…This [treatment] protocol is based on:\n- American [Diabetes] Association Standards of Care in [Diabetes] (2024)\n- CDC…",
          "text": " pain, confusion)\n- Severe hypoglycemia requiring assistance\n- Acute complications (MI, stroke, foot infection)\n- Inability to care for self safely\n\n### 4.11 Medication Assistance and Resources\n\nFinancial support:\n- Pharmaceutical patient assistance programs\n- 340B drug pricing if eligible\n- Manufacturer coupons and savings cards\n- State medication assistance programs\n- Community health center referral if uninsured\n\nEquipment and supplies:\n- CGM coverage verification and prior authorization assistance\n- Insulin pump coverage if indicated\n- Blood glucose meter and strip coverage\n- Sharps disposal containers\n- Diabetic shoe program (Medicare Part B)\n\nCommunity resources:\n- Transportation services (medical appointments)\n- Meal delivery programs\n- Home health aide services\n- Diabetes education programs\n- Exercise programs for seniors/disabled\n\n---\n\n## References and Guidelines\n\nThis treatment protocol is based on:\n- American Diabetes Association Standards of Care in Diabetes (2024)\n- CDC National Diabetes Statistics Report (2023)\n- Endocrine Society Clinical Practice Guidelines\n- AACE/ACE Comprehensive Type 2 Diabetes Management Algorithm\n- AHA/ACC Guideline on the Primary Prevention o"
        },
        {
          "doc_id": "cdc-diabetes-treatment-guidelines",
          "title": "CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES",
          "chunk_id": 0,
          "score": 3.162101192394457e-06,
          "snippet": "# CDC [DIABETES] COMPLICATION RISK MANAGEMENT GUIDELINES\nEvidence-Based [Treatment] Protocols\n\n## Section 1: LOW RISK PATIENTS (0…",
          "text": "# CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\nEvidence-Based Treatment Protocols\n\n## Section 1: LOW RISK PATIENTS (0-30% Complication Probability)\n\n### 1.1 ICD-10-CM Coding\n- E11.9: Type 2 diabetes mellitus without complications\n- Z79.4: Long-term (current) use of insulin (if applicable)\n- E11.00: Type 2 diabetes with hyperosmolarity without coma (if applicable)\n\n### 1.2 Treatment Goals\n- HbA1c target: <7.0% (individualized based on patient factors)\n- Fasting plasma glucose: 80-130 mg/dL\n- Postprandial glucose: <180 mg/dL\n- Blood pressure: <140/90 mmHg\n- LDL cholesterol: <100 mg/dL\n\n### 1.3 Medication Management\nFirst-line therapy:\n- Metformin 500-2000 mg daily (if eGFR >30 mL/min)\n- Lifestyle modifications as foundation\n\nAdditional agents if needed:\n- GLP-1 receptor agonist for cardiovascular benefit\n- SGLT2 inhibitor for renal and cardiac protection\n- DPP-4 inhibitor as alternative\n\n### 1.4 Monitoring Schedule\n- Clinic visits: Every 3-6 months\n- HbA1c testing: Every 6 months if stable, every 3 months if not at goal\n- Self-monitoring blood glucose: As clinically indicated\n- Annual comprehensive metabolic panel\n- Annual lipid panel\n\n### 1.5 Preventive Screening\nAnnual scre"
        },
        {
          "doc_id": "cdc-diabetes-treatment-guidelines",
          "title": "CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES",
          "chunk_id": 1,
          "score": 3.1004835799350414e-06,
          "snippet": "…Type 2 [diabetes] with chronic kidney disease (if applicable)\n\n### 2.2 Enhanced [Treatment] Goals\n- HbA1c target…",
          "text": " if stable, every 3 months if not at goal\n- Self-monitoring blood glucose: As clinically indicated\n- Annual comprehensive metabolic panel\n- Annual lipid panel\n\n### 1.5 Preventive Screening\nAnnual screenings required:\n- Dilated comprehensive eye examination\n- Urine albumin-to-creatinine ratio\n- Serum creatinine and estimated GFR\n- Comprehensive foot examination\n- Dental examination\n\n### 1.6 Patient Education\n- Diabetes self-management education (DSME)\n- Medical nutrition therapy\n- Physical activity counseling (150 min/week moderate intensity)\n- Recognition of hypoglycemia and hyperglycemia\n- Sick-day management\n- Foot care education\n\n### 1.7 Vaccinations\n- Influenza vaccine annually\n- Pneumococcal vaccine per CDC guidelines\n- COVID-19 vaccination and boosters\n- Hepatitis B vaccine for adults <60 years\n\n---\n\n## Section 2: MODERATE RISK PATIENTS (30-60% Complication Probability)\n\n### 2.1 ICD-10-CM Coding\n- E11.65: Type 2 diabetes mellitus with hyperglycemia\n- E11.9: Type 2 diabetes mellitus without complications\n- Z79.4: Long-term (current) use of insulin\n- E11.22: Type 2 diabetes with chronic kidney disease (if applicable)\n\n### 2.2 Enhanced Treatment Goals\n- HbA1c target: <7.0% (cons"
        }
      ]
    },
    "isError": false
  }
}

 C:\Users\davidzhang\Downloads\ml\ml\doc_mcp_1>python client.py --search "diabetes treatment" --top-k 5
[doc_mcp_server] Loaded 1 docs. FTS5=yes
[doc_mcp_server] Ready.
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"query\": \"diabetes treatment\",\n  \"top_k\": 5,\n  \"matches\": [\n    {\n      \"doc_id\": \"cdc-diabetes-treatment-guidelines\",\n      \"title\": \"CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\",\n      \"chunk_id\": 3,\n      \"score\": 3.3014800093648174e-06,\n      \"snippet\": \"…Type 2 [diabetes] with circulatory complications\\n- I50.9: Heart failure (if present)\\n\\n### 3.2 Aggressive [Treatment]…\",\n      \"text\": \"itoring (CGM)\\n- Kidney function testing: Every 6 months\\n- Eye examination: Every 6-12 months\\n\\n### 2.5 Enhanced Interventions\\n- Referral to certified diabetes care and education specialist\\n- Quarterly nutritionist consultations\\n- Structured exercise program\\n- Cardiovascular risk assessment\\n- Sleep apnea screening if indicated\\n- Depression and diabetes distress screening\\n\\n### 2.6 Complication Screening\\nBiannual assessments:\\n- Comprehensive foot examination\\n- Monofilament testing for neuropathy\\n- Ankle-brachial index if claudication symptoms\\n- Retinal photography or dilated eye exam\\n\\n---\\n\\n## Section 3: HIGH RISK PATIENTS (60-80% Complication Probability)\\n\\n### 3.1 ICD-10-CM Coding\\nPrimary codes:\\n- E11.65: Type 2 diabetes with hyperglycemia\\n- E11.69: Type 2 diabetes with other specified complication\\n- E11.8: Type 2 diabetes with unspecified complications\\n\\nComplication-specific codes as identified:\\n- E11.21: Type 2 diabetes with diabetic nephropathy\\n- E11.311-319: Type 2 diabetes with diabetic retinopathy\\n- E11.40-49: Type 2 diabetes with diabetic neuropathy\\n- E11.51-59: Type 2 diabetes with circulatory complications\\n- I50.9: Heart failure (if present)\\n\\n### 3.2 Aggressive Treatment Goals\"\n    },\n    {\n      \"doc_id\": \"cdc-diabetes-treatment-guidelines\",\n      \"title\": \"CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\",\n      \"chunk_id\": 15,\n      \"score\": 3.258944413339537e-06,\n      \"snippet\": \"ational [Diabetes] Statistics Report (2023)\\n- Endocrine Society Clinical Practice Guidelines\\n- AACE/ACE Comprehensive Type 2 [Diabetes]…\",\n      \"text\": \"ational Diabetes Statistics Report (2023)\\n- Endocrine Society Clinical Practice Guidelines\\n- AACE/ACE Comprehensive Type 2 Diabetes Management Algorithm\\n- AHA/ACC Guideline on the Primary Prevention of Cardiovascular Disease\\n- KDIGO Clinical Practice Guideline for Diabetes Management in CKD\\n- ICD-10-CM Official Guidelines for Coding and Reporting (2024)\\n\\nLast Updated: January 2026\"\n    },\n    {\n      \"doc_id\": \"cdc-diabetes-treatment-guidelines\",\n      \"title\": \"CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\",\n      \"chunk_id\": 14,\n      \"score\": 3.2282155449534986e-06,\n      \"snippet\": \"…This [treatment] protocol is based on:\\n- American [Diabetes] Association Standards of Care in [Diabetes] (2024)\\n- CDC…\",\n      \"text\": \" pain, confusion)\\n- Severe hypoglycemia requiring assistance\\n- Acute complications (MI, stroke, foot infection)\\n- Inability to care for self safely\\n\\n### 4.11 Medication Assistance and Resources\\n\\nFinancial support:\\n- Pharmaceutical patient assistance programs\\n- 340B drug pricing if eligible\\n- Manufacturer coupons and savings cards\\n- State medication assistance programs\\n- Community health center referral if uninsured\\n\\nEquipment and supplies:\\n- CGM coverage verification and prior authorization assistance\\n- Insulin pump coverage if indicated\\n- Blood glucose meter and strip coverage\\n- Sharps disposal containers\\n- Diabetic shoe program (Medicare Part B)\\n\\nCommunity resources:\\n- Transportation services (medical appointments)\\n- Meal delivery programs\\n- Home health aide services\\n- Diabetes education programs\\n- Exercise programs for seniors/disabled\\n\\n---\\n\\n## References and Guidelines\\n\\nThis treatment protocol is based on:\\n- American Diabetes Association Standards of Care in Diabetes (2024)\\n- CDC National Diabetes Statistics Report (2023)\\n- Endocrine Society Clinical Practice Guidelines\\n- AACE/ACE Comprehensive Type 2 Diabetes Management Algorithm\\n- AHA/ACC Guideline on the Primary Prevention o\"\n    },\n    {\n      \"doc_id\": \"cdc-diabetes-treatment-guidelines\",\n      \"title\": \"CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\",\n      \"chunk_id\": 0,\n      \"score\": 3.162101192394457e-06,\n      \"snippet\": \"# CDC [DIABETES] COMPLICATION RISK MANAGEMENT GUIDELINES\\nEvidence-Based [Treatment] Protocols\\n\\n## Section 1: LOW RISK PATIENTS (0…\",\n      \"text\": \"# CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\\nEvidence-Based Treatment Protocols\\n\\n## Section 1: LOW RISK PATIENTS (0-30% Complication Probability)\\n\\n### 1.1 ICD-10-CM Coding\\n- E11.9: Type 2 diabetes mellitus without complications\\n- Z79.4: Long-term (current) use of insulin (if applicable)\\n- E11.00: Type 2 diabetes with hyperosmolarity without coma (if applicable)\\n\\n### 1.2 Treatment Goals\\n- HbA1c target: <7.0% (individualized based on patient factors)\\n- Fasting plasma glucose: 80-130 mg/dL\\n- Postprandial glucose: <180 mg/dL\\n- Blood pressure: <140/90 mmHg\\n- LDL cholesterol: <100 mg/dL\\n\\n### 1.3 Medication Management\\nFirst-line therapy:\\n- Metformin 500-2000 mg daily (if eGFR >30 mL/min)\\n- Lifestyle modifications as foundation\\n\\nAdditional agents if needed:\\n- GLP-1 receptor agonist for cardiovascular benefit\\n- SGLT2 inhibitor for renal and cardiac protection\\n- DPP-4 inhibitor as alternative\\n\\n### 1.4 Monitoring Schedule\\n- Clinic visits: Every 3-6 months\\n- HbA1c testing: Every 6 months if stable, every 3 months if not at goal\\n- Self-monitoring blood glucose: As clinically indicated\\n- Annual comprehensive metabolic panel\\n- Annual lipid panel\\n\\n### 1.5 Preventive Screening\\nAnnual scre\"\n    },\n    {\n      \"doc_id\": \"cdc-diabetes-treatment-guidelines\",\n      \"title\": \"CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\",\n      \"chunk_id\": 1,\n      \"score\": 3.1004835799350414e-06,\n      \"snippet\": \"…Type 2 [diabetes] with chronic kidney disease (if applicable)\\n\\n### 2.2 Enhanced [Treatment] Goals\\n- HbA1c target…\",\n      \"text\": \" if stable, every 3 months if not at goal\\n- Self-monitoring blood glucose: As clinically indicated\\n- Annual comprehensive metabolic panel\\n- Annual lipid panel\\n\\n### 1.5 Preventive Screening\\nAnnual screenings required:\\n- Dilated comprehensive eye examination\\n- Urine albumin-to-creatinine ratio\\n- Serum creatinine and estimated GFR\\n- Comprehensive foot examination\\n- Dental examination\\n\\n### 1.6 Patient Education\\n- Diabetes self-management education (DSME)\\n- Medical nutrition therapy\\n- Physical activity counseling (150 min/week moderate intensity)\\n- Recognition of hypoglycemia and hyperglycemia\\n- Sick-day management\\n- Foot care education\\n\\n### 1.7 Vaccinations\\n- Influenza vaccine annually\\n- Pneumococcal vaccine per CDC guidelines\\n- COVID-19 vaccination and boosters\\n- Hepatitis B vaccine for adults <60 years\\n\\n---\\n\\n## Section 2: MODERATE RISK PATIENTS (30-60% Complication Probability)\\n\\n### 2.1 ICD-10-CM Coding\\n- E11.65: Type 2 diabetes mellitus with hyperglycemia\\n- E11.9: Type 2 diabetes mellitus without complications\\n- Z79.4: Long-term (current) use of insulin\\n- E11.22: Type 2 diabetes with chronic kidney disease (if applicable)\\n\\n### 2.2 Enhanced Treatment Goals\\n- HbA1c target: <7.0% (cons\"\n    }\n  ]\n}"
      }
    ],
    "structuredContent": {
      "query": "diabetes treatment",
      "top_k": 5,
      "matches": [
        {
          "doc_id": "cdc-diabetes-treatment-guidelines",
          "title": "CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES",
          "chunk_id": 3,
          "score": 3.3014800093648174e-06,
          "snippet": "…Type 2 [diabetes] with circulatory complications\n- I50.9: Heart failure (if present)\n\n### 3.2 Aggressive [Treatment]…",
          "text": "itoring (CGM)\n- Kidney function testing: Every 6 months\n- Eye examination: Every 6-12 months\n\n### 2.5 Enhanced Interventions\n- Referral to certified diabetes care and education specialist\n- Quarterly nutritionist consultations\n- Structured exercise program\n- Cardiovascular risk assessment\n- Sleep apnea screening if indicated\n- Depression and diabetes distress screening\n\n### 2.6 Complication Screening\nBiannual assessments:\n- Comprehensive foot examination\n- Monofilament testing for neuropathy\n- Ankle-brachial index if claudication symptoms\n- Retinal photography or dilated eye exam\n\n---\n\n## Section 3: HIGH RISK PATIENTS (60-80% Complication Probability)\n\n### 3.1 ICD-10-CM Coding\nPrimary codes:\n- E11.65: Type 2 diabetes with hyperglycemia\n- E11.69: Type 2 diabetes with other specified complication\n- E11.8: Type 2 diabetes with unspecified complications\n\nComplication-specific codes as identified:\n- E11.21: Type 2 diabetes with diabetic nephropathy\n- E11.311-319: Type 2 diabetes with diabetic retinopathy\n- E11.40-49: Type 2 diabetes with diabetic neuropathy\n- E11.51-59: Type 2 diabetes with circulatory complications\n- I50.9: Heart failure (if present)\n\n### 3.2 Aggressive Treatment Goals"
        },
        {
          "doc_id": "cdc-diabetes-treatment-guidelines",
          "title": "CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES",
          "chunk_id": 15,
          "score": 3.258944413339537e-06,
          "snippet": "ational [Diabetes] Statistics Report (2023)\n- Endocrine Society Clinical Practice Guidelines\n- AACE/ACE Comprehensive Type 2 [Diabetes]…",
          "text": "ational Diabetes Statistics Report (2023)\n- Endocrine Society Clinical Practice Guidelines\n- AACE/ACE Comprehensive Type 2 Diabetes Management Algorithm\n- AHA/ACC Guideline on the Primary Prevention of Cardiovascular Disease\n- KDIGO Clinical Practice Guideline for Diabetes Management in CKD\n- ICD-10-CM Official Guidelines for Coding and Reporting (2024)\n\nLast Updated: January 2026"
        },
        {
          "doc_id": "cdc-diabetes-treatment-guidelines",
          "title": "CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES",
          "chunk_id": 14,
          "score": 3.2282155449534986e-06,
          "snippet": "…This [treatment] protocol is based on:\n- American [Diabetes] Association Standards of Care in [Diabetes] (2024)\n- CDC…",
          "text": " pain, confusion)\n- Severe hypoglycemia requiring assistance\n- Acute complications (MI, stroke, foot infection)\n- Inability to care for self safely\n\n### 4.11 Medication Assistance and Resources\n\nFinancial support:\n- Pharmaceutical patient assistance programs\n- 340B drug pricing if eligible\n- Manufacturer coupons and savings cards\n- State medication assistance programs\n- Community health center referral if uninsured\n\nEquipment and supplies:\n- CGM coverage verification and prior authorization assistance\n- Insulin pump coverage if indicated\n- Blood glucose meter and strip coverage\n- Sharps disposal containers\n- Diabetic shoe program (Medicare Part B)\n\nCommunity resources:\n- Transportation services (medical appointments)\n- Meal delivery programs\n- Home health aide services\n- Diabetes education programs\n- Exercise programs for seniors/disabled\n\n---\n\n## References and Guidelines\n\nThis treatment protocol is based on:\n- American Diabetes Association Standards of Care in Diabetes (2024)\n- CDC National Diabetes Statistics Report (2023)\n- Endocrine Society Clinical Practice Guidelines\n- AACE/ACE Comprehensive Type 2 Diabetes Management Algorithm\n- AHA/ACC Guideline on the Primary Prevention o"
        },
        {
          "doc_id": "cdc-diabetes-treatment-guidelines",
          "title": "CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES",
          "chunk_id": 0,
          "score": 3.162101192394457e-06,
          "snippet": "# CDC [DIABETES] COMPLICATION RISK MANAGEMENT GUIDELINES\nEvidence-Based [Treatment] Protocols\n\n## Section 1: LOW RISK PATIENTS (0…",
          "text": "# CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES\nEvidence-Based Treatment Protocols\n\n## Section 1: LOW RISK PATIENTS (0-30% Complication Probability)\n\n### 1.1 ICD-10-CM Coding\n- E11.9: Type 2 diabetes mellitus without complications\n- Z79.4: Long-term (current) use of insulin (if applicable)\n- E11.00: Type 2 diabetes with hyperosmolarity without coma (if applicable)\n\n### 1.2 Treatment Goals\n- HbA1c target: <7.0% (individualized based on patient factors)\n- Fasting plasma glucose: 80-130 mg/dL\n- Postprandial glucose: <180 mg/dL\n- Blood pressure: <140/90 mmHg\n- LDL cholesterol: <100 mg/dL\n\n### 1.3 Medication Management\nFirst-line therapy:\n- Metformin 500-2000 mg daily (if eGFR >30 mL/min)\n- Lifestyle modifications as foundation\n\nAdditional agents if needed:\n- GLP-1 receptor agonist for cardiovascular benefit\n- SGLT2 inhibitor for renal and cardiac protection\n- DPP-4 inhibitor as alternative\n\n### 1.4 Monitoring Schedule\n- Clinic visits: Every 3-6 months\n- HbA1c testing: Every 6 months if stable, every 3 months if not at goal\n- Self-monitoring blood glucose: As clinically indicated\n- Annual comprehensive metabolic panel\n- Annual lipid panel\n\n### 1.5 Preventive Screening\nAnnual scre"
        },
        {
          "doc_id": "cdc-diabetes-treatment-guidelines",
          "title": "CDC DIABETES COMPLICATION RISK MANAGEMENT GUIDELINES",
          "chunk_id": 1,
          "score": 3.1004835799350414e-06,
          "snippet": "…Type 2 [diabetes] with chronic kidney disease (if applicable)\n\n### 2.2 Enhanced [Treatment] Goals\n- HbA1c target…",
          "text": " if stable, every 3 months if not at goal\n- Self-monitoring blood glucose: As clinically indicated\n- Annual comprehensive metabolic panel\n- Annual lipid panel\n\n### 1.5 Preventive Screening\nAnnual screenings required:\n- Dilated comprehensive eye examination\n- Urine albumin-to-creatinine ratio\n- Serum creatinine and estimated GFR\n- Comprehensive foot examination\n- Dental examination\n\n### 1.6 Patient Education\n- Diabetes self-management education (DSME)\n- Medical nutrition therapy\n- Physical activity counseling (150 min/week moderate intensity)\n- Recognition of hypoglycemia and hyperglycemia\n- Sick-day management\n- Foot care education\n\n### 1.7 Vaccinations\n- Influenza vaccine annually\n- Pneumococcal vaccine per CDC guidelines\n- COVID-19 vaccination and boosters\n- Hepatitis B vaccine for adults <60 years\n\n---\n\n## Section 2: MODERATE RISK PATIENTS (30-60% Complication Probability)\n\n### 2.1 ICD-10-CM Coding\n- E11.65: Type 2 diabetes mellitus with hyperglycemia\n- E11.9: Type 2 diabetes mellitus without complications\n- Z79.4: Long-term (current) use of insulin\n- E11.22: Type 2 diabetes with chronic kidney disease (if applicable)\n\n### 2.2 Enhanced Treatment Goals\n- HbA1c target: <7.0% (cons"
        }
      ]
    },
    "isError": false
  }
}


 C:\Users\davidzhang\Downloads\ml\ml\doc_mcp_1>python client.py --search "hypertension guidelines" --top-k 10 **--output results.json**
[doc_mcp_server] Loaded 1 docs. FTS5=yes
[doc_mcp_server] Ready.
Results written to results.json
