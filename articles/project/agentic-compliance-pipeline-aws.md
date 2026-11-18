---
title: Separating Deterministic Data Engineering from Probabilistic AI: Building an Event-Driven Agentic Compliance Pipeline on AWS
author: Krishna Prasad Chapagain
date: 2026-11-18
summary: A reference architecture that keeps deterministic data engineering — schema validation, PII tokenization, encryption, and guardrails — strictly separated from probabilistic agent reasoning, using EventBridge, SQS, Lambda, and Amazon Bedrock for AML and fraud triage in financial services.
slug: agentic-compliance-pipeline-aws
tags: ["Data Engineering", "Agentic AI", "AWS", "Terraform", "FinTech", "Responsible AI"]
repo: https://github.com/entertainingrover01/aws-agentic-compliance-pipeline
---

# Separating Deterministic Data Engineering from Probabilistic AI: Building an Event-Driven Agentic Compliance Pipeline on AWS

Most AI agent demos look impressive in a local notebook—an LLM connects directly to a database, runs a few queries, and prints a confident answer. In a regulated financial institution, that exact pattern is a non-starter.

Banks cannot allow probabilistic models to query raw production databases, ingest unmasked Personally Identifiable Information (PII), or write unverified decisions directly to downstream systems. When I set out to build a reference architecture for Data Engineering for Agentic Workflows, my goal was to design a system that treats AI agents the way financial institutions treat any other untrusted downstream service: isolated, decoupled, governed, and fully auditable.

You can explore the complete, deployable Infrastructure-as-Code (IaC) repository on GitHub: [aws-agentic-compliance-pipeline](https://github.com/entertainingrover01/aws-agentic-compliance-pipeline).

## The Core Design Philosophy

Instead of giving an AI agent broad access to raw data, this pipeline enforces a strict boundary between deterministic data engineering (schema validation, PII tokenization, encryption, and output guardrails) and probabilistic agent reasoning (AML/fraud pattern triage via Amazon Bedrock).

```flowchart
flowchart LR
    subgraph IaC["Provisioned & Governed via Terraform IaC"]
        A[Raw Transactions<br/>S3 Raw Bucket<br/>KMS Encrypted] -->|Object Created| B[Amazon EventBridge]
        B --> C[Lambda: Ingest & Mask<br/>Schema Validation + SHA-256 PII Redaction]
        C -->|Clean Records| D[S3 Curated Bucket<br/>KMS Encrypted]
        C -->|Async Task| E[Amazon SQS<br/>+ Dead Letter Queue]
        E --> F[Lambda: Agentic Reviewer<br/>Amazon Bedrock Converse API]
        F -->|Post-LLM Guardrail<br/>Schema + Confidence Check| G[S3 Audit Bucket<br/>Partitioned JSON]
        G --> H[AWS Glue Catalog +<br/>Amazon Athena SQL Audit]
    end
```

## 4 Engineering Decisions That Matter for Financial Services

1. Infrastructure as Code (IaC) Over "ClickOps"

In enterprise banking, manually clicking through the AWS Console creates undocumented security gaps and configuration drift. Every resource in this pipeline—four S3 buckets, a customer-managed KMS key, EventBridge rules, SQS queues, IAM roles, Lambda functions, and Glue/Athena tables—is provisioned via modular Terraform.

Version-Controlled Audit Trail: Every IAM permission and bucket policy lives in Git and can be reviewed before deployment.

Security by Default: S3 BlockPublicAccess, customer-managed KMS encryption (aws:kms), and least-privilege IAM roles (separate roles for ingestion vs. agent inference) are enforced automatically.

Reproducibility: The entire stack deploys or tears down deterministically in minutes with zero orphaned resources.

2. Zero-PII Agent Context

When a raw transaction file lands in S3, Amazon EventBridge triggers a deterministic Python Lambda (ingest_and_mask). Before any data is queued for the AI agent:

Required schema fields are strictly validated.

Sensitive identifiers (account_number, customer_ssn) are deterministically tokenized using salted SHA-256 hashing.

Direct identifiers (customer_name) are stripped completely.

The downstream agent receives enough behavioral context (amounts, timestamps, jurisdictions, velocity notes) to flag anomalies like sub-$10,000 structuring, without ever seeing raw customer PII.

3. Resilient Decoupling with EventBridge & SQS

LLM APIs have higher latency and stricter rate limits than traditional ETL jobs. Placing Amazon SQS (backed by a Dead Letter Queue) between the ingestion layer and the agentic reviewer decouples data ingestion from model inference. If traffic spikes or Bedrock throttles, transactions are safely buffered and retried rather than dropped.

4. Post-LLM Deterministic Guardrails & Human-in-the-Loop Escalation

LLMs can hallucinate JSON keys or return overconfident answers. Inside the agentic_reviewer Lambda, every response from the Amazon Bedrock Converse API passes through a deterministic Python guardrail layer before it is written to the audit lake:

Schema Enforcement: Verifies the decision is strictly one of APPROVE, FLAG_FOR_REVIEW, or BLOCK_AND_ESCALATE, with a valid 0–100 risk score.

Automatic Human Escalation: Any transaction with confidence < 0.80, risk_score >= 60, or a non-APPROVE verdict automatically sets requires_human_review = true.

Fail-Safe Fallback: If the model returns malformed output, the guardrail catches the exception, flags the transaction with guardrail_status = "FALLBACK_TRIGGERED", and routes it for human review.

## Queryable Audit Lineage with Glue & Athena

Compliance teams need SQL-level visibility into why an agent made a decision and which model version made it. Every evaluated transaction is written to the encrypted Audit S3 bucket as date-partitioned newline-delimited JSON (dt=YYYY-MM-DD) containing batch_id, model_id, risk_score, confidence, guardrail_status, and rationale.

With AWS Glue Partition Projection configured in Terraform, compliance analysts can query agent decisions in Amazon Athena immediately—no crawlers required:

```sql
SELECT
  transaction_id,
  decision,
  risk_score,
  confidence,
  requires_human_review,
  guardrail_status,
  rationale
FROM agentic_compliance_dev.agent_decisions
WHERE dt = '2026-11-18'
ORDER BY risk_score DESC;
```

## Try It Yourself

The entire pipeline is open-source and uses zero external Python dependencies (native boto3 + Terraform), so you can deploy, run the synthetic AML structuring test, and tear it down in under 10 minutes:

```bash
git clone https://github.com/entertainingrover01/aws-agentic-compliance-pipeline.git
cd aws-agentic-compliance-pipeline/terraform
terraform init && terraform apply -auto-approve

cd ..
./scripts/run_demo.sh
```

Building reliable agentic systems isn't just about prompt engineering—it's about data engineering, security boundaries, and auditability. Separating what must be deterministic from what can be probabilistic is how we move AI agents from fragile prototypes to production-ready financial infrastructure.
