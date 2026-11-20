---
title: Data Engineering in the Agentic Era: What the Modern Data Engineer Actually Does (Day 1 of 30)
author: Krishna Prasad Chapagain
date: 2026-11-20
summary: November 2026 made it official — agents are now first-class data consumers. Day 1 of a 30-day plan maps what the modern data engineer actually does, and the AWS, Azure, and GCP skills the next 29 days will build.
slug: day-01-data-engineering-agentic-era
tags: ["Data Engineering", "Agentic AI", "AWS", "Azure", "GCP", "Learning"]
---

# Data Engineering in the Agentic Era: What the Modern Data Engineer Actually Does (Day 1 of 30)

*This is Day 1 of a 30-day plan to learn data engineering across AWS, Azure, and GCP — one article a day, each ending with something to build. Today: the landscape, and why the job changed.*

## What changed this month

November 2026 has been a month of announcements that all point the same way: AI agents are no longer demos. They are production workloads — and production workloads need governed data.

- **November 5:** AWS made Web Answer generally available on Bedrock AgentCore, and made Kiro bots generally available in Kiro Crew — agents that own ongoing coding responsibilities, including the kind of pipeline and SQL work data engineers do every day.
- **November 11:** AWS launched a standalone Web Search API for Bedrock AgentCore (`InvokeWebSearch`, $7 per 1,000 queries, plain IAM auth) — explicitly pitched at custom agent loops *and* at data pipelines: enrichment, fact-checking, and monitoring workloads that need retrieval without leaving AWS.
- **November 17:** Microsoft announced Agent 365, giving agents from Salesforce, Amazon, Google, Databricks, Snowflake, Anthropic, and OpenAI their own Entra Agent ID — agents as governed identities, with managers and permissions, like employees.
- **November 18:** Google launched Gemini 4 Neon for long-running agent work.
- **December 1:** AWS CEO Matt Garman keynotes re:Invent 2026 on "the agentic era."

The pattern is hard to miss. Every cloud vendor is racing to make agents deployable, governable, and billable. And every agent they deploy will need the same thing: clean, governed, well-modeled data, delivered through interfaces it cannot abuse.

That is the data engineer's job now. It always was — the consumers just got stranger.

## What the modern data engineer actually does

Strip away the job descriptions and the work has an enduring core:

1. **Model the data.** Star schemas, Data Vault, medallion architecture — the decisions about how data is shaped determine everything downstream. An agent querying a well-modeled warehouse gets good answers; one querying a swamp gets confident wrong ones.
2. **Move the data.** Batch ingestion, streaming, CDC — getting data from source systems into the lake and warehouse reliably, with retries, idempotency, and observability.
3. **Transform it.** SQL and Python pipelines that turn raw events into trusted tables: dbt models, Spark jobs, Glue jobs, Dataflow pipelines.
4. **Prove it's good.** Tests, freshness checks, data quality monitoring. A pipeline that silently ships wrong data is worse than one that fails loudly.
5. **Govern it.** Who can see what, which columns are PII, where the lineage leads. In financial services this is the job, not a side quest.

What the agentic era adds is a sixth responsibility: **building the interfaces agents use.** Guardrailed NL-to-SQL, validated agent-generated SQL, audit-logged inference — the work I wrote about in the [agentic compliance pipeline](/blog/agentic-compliance-pipeline-aws/), the [Kiro database workflow](/blog/kiro-agentic-database-workflow/), and the [governed NL-to-SQL layer](/blog/governed-nl-to-sql-analytics/) projects. The agent is a new kind of downstream consumer, and it needs the same treatment as any other untrusted service: isolated, decoupled, governed, and fully auditable.

## The three-cloud map

This plan covers all three major clouds, because real data teams are rarely single-cloud — and because the concepts transfer even when the service names don't:

| Layer | AWS | Azure | GCP |
|---|---|---|---|
| Object storage / lake | S3 | ADLS Gen2 | Cloud Storage |
| Serverless SQL | Athena | Synapse serverless | BigQuery |
| Warehouse | Redshift | Synapse / Fabric | BigQuery |
| ETL / Spark | Glue, EMR | Data Factory, Databricks | Dataflow, Dataproc |
| Streaming | Kinesis, MSK | Event Hubs | Pub/Sub |
| Orchestration | Step Functions, MWAA | Data Factory | Composer, Workflows |
| Agent platform | Bedrock AgentCore | Foundry / Agent 365 | Vertex AI |

Learn one column deeply and the other two become translation exercises. That is the plan: AWS first (Weeks 1–2), then Azure and GCP (Week 3), then the advanced topics that sit above all three (Week 4).

## The 30-day plan

- **Week 1 — Foundations:** the modern stack, SQL beyond SELECT, data modeling, Python for pipelines, object storage, ingestion patterns, and a mini lakehouse project.
- **Week 2 — AWS deep dive:** Glue, Athena, Redshift, EMR/Spark, Kinesis/MSK, Step Functions/MWAA, and an end-to-end AWS pipeline project.
- **Week 3 — Azure & GCP:** Data Factory, Synapse, Databricks, Fabric, BigQuery, Dataflow/Beam, Dataproc/Pub/Sub — and the same pipeline built on all three clouds, compared.
- **Week 4 — Advanced & agentic:** dbt, data quality and observability, Kafka/Flink streaming, Delta/Iceberg/Hudi, governance, agentic SQL with guardrails, governed NL-to-SQL, Terraform for data platforms — and a capstone platform design.

## Day 1 exercise: set up your lab (30 minutes)

1. Install Python 3.12 and a virtual-environment tool. Verify with `python3 --version`.
2. Install the AWS CLI and Git. Create (or confirm) an AWS free-tier account and configure a profile.
3. Install DuckDB (`pip install duckdb`) — it will be our local stand-in for a warehouse all month.
4. Pick a dataset you care about — NYC taxi trips, a Kaggle retail dataset, anything with a few hundred thousand rows — and download it locally.
5. Sketch, on paper or in a notebook, the medallion version of it: what would your bronze (raw), silver (cleaned), and gold (analytics-ready) layers contain? Keep the sketch; Day 7 builds it.

Tomorrow, Day 2: SQL for data engineering — window functions, CTEs, and reading a query plan like an engineer, not a analyst.
