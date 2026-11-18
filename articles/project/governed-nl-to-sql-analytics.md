---
title: A Governed NL-to-SQL Analytics Layer on AWS: Plain-English Questions, Read-Only Answers
author: Krishna Prasad Chapagain
date: 2026-11-18
summary: A lightweight, read-only agentic analytics layer on a retail Postgres dataset — ask a question in plain English, and a visible guardrail layer blocks mutating statements, enforces strict schema boundaries, and logs every generated SQL query for audit review before returning results.
slug: governed-nl-to-sql-analytics
tags: ["Data Engineering", "Agentic AI", "AWS", "Bedrock", "Terraform", "PostgreSQL", "Responsible AI"]
repo: https://github.com/entertainingrover01/aws-governed-nl-to-sql-analytics
---

# A Governed NL-to-SQL Analytics Layer on AWS: Plain-English Questions, Read-Only Answers

Ask a question in plain English, get an answer from a Postgres database — without ever letting the language model run arbitrary SQL.

Most NL-to-SQL demos hand the model a database connection and hope for the best. In a regulated environment that is a non-starter: a probabilistic model must never be able to `DROP` a table, `SELECT` from a table it was never shown, or dump a million rows. This project treats the model as an untrusted downstream service and puts three independent, deterministic layers between it and the data.

You can explore the complete repository on GitHub: [aws-governed-nl-to-sql-analytics](https://github.com/entertainingrover01/aws-governed-nl-to-sql-analytics).

## How it works

A demo widget (a static site on S3) sends your question to an API Gateway HTTP API, which calls a Lambda. The Lambda asks Amazon Bedrock (Claude Sonnet 4.5) to turn the question into SQL — then, before that SQL goes anywhere near the database, it is validated by a deterministic guardrail layer. Only allowed SQL runs, and only against a read-only database user. Every request is written to a DynamoDB audit log before the response is returned.

```flowchart
flowchart LR
    User([User]) -->|Question| Widget[Demo widget<br/>S3 static website]
    Widget -->|POST /ask| API[API Gateway<br/>HTTP API]
    API --> Lambda[Lambda: nl_to_sql<br/>Python 3.12, in VPC]
    Lambda -->|Converse API| Bedrock[Amazon Bedrock<br/>Claude Sonnet 4.5]
    Bedrock -->|Generated SQL| Lambda
    Lambda -->|validate| Guardrails[Guardrails<br/>deterministic, stdlib only]
    Guardrails -->|BLOCKED| Audit[(DynamoDB audit log)]
    Guardrails -->|ALLOWED| DB[(Postgres<br/>RDS or Supabase<br/>read-only user)]
    DB -->|Rows| Lambda
    Lambda -->|audit record| Audit
    Lambda -->|JSON results| API
    API -->|Results| Widget
```

## The three layers between the model and the data

**1. Guardrails — every generated statement is validated before it is allowed near the database.** Only a single `SELECT` (or `WITH ... SELECT`) is permitted. Mutating keywords are blocked — `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `GRANT`, `REVOKE`, `COPY`, `CREATE`, `INTO`, `MERGE`, `CALL`, `DO`, `VACUUM`, `ANALYZE`, `COMMENT`, `SECURITY` — and string literals are stripped before scanning, so a product named `'DROP'` is fine. System catalogs (`information_schema`, `pg_catalog`) are forbidden, including via `UNION`. Tables and columns must exist in the schema (`stores`, `products`, `inventory`, `customers`, `sales`) or be a CTE defined in the query. A missing `LIMIT` gets `LIMIT 100` appended; a larger `LIMIT` is capped at 100.

**2. Least-privilege role — the Lambda connects as `analytics_ro`, a Postgres user with `SELECT` and nothing else.** Even if a guardrail were bypassed, the database user itself cannot write.

**3. Read-only transaction — every execution starts with `SET TRANSACTION READ ONLY`, with a 10-second statement timeout.** Defence in depth, not a single point of trust.

## Audit log: every question, on the record

One DynamoDB item per request — allowed, blocked, or errored — records the question, the generated SQL, the guardrail verdict (`ALLOWED` / `BLOCKED` / `ERROR`), the guardrail reason, the model id, the row count, and the execution time. There is a complete record of what was asked, what SQL was generated, what the guardrails decided, and how many rows came back. That is the piece most NL-to-SQL demos skip, and the piece a compliance team asks for first.

## Try it: demo questions

Allowed (run against the seed retail data):

- "What are the top 5 products by total sales revenue?"
- "Which store made the most revenue in October 2026?"
- "How many Gold loyalty customers do we have?"
- "Show me inventory below 10 units by store."

Blocked by the guardrails:

- "Delete all sales from last year" — the model generates a `DELETE`, which is not a `SELECT`.
- "How many employees work in each department?" — there is no `employees` table; the model hallucinates one and the table allowlist blocks it.

The blocked cases depend on the model generating the disallowed SQL — the questions are phrased to elicit it, and in practice it does. The deterministic behaviour of the guardrails does not depend on the model at all and is covered by the test suite: 30 stdlib unittest tests for every guardrail rule, no AWS access or database needed.

## Deploy

The repo is modular Terraform (AWS provider ~> 5.0): HTTP API, Lambda with a psycopg2 layer in the VPC, DynamoDB audit table (pay-per-request), Postgres 16 on RDS (`db.t3.micro`, encrypted, private), the connection string in Secrets Manager, S3 hosting for the demo widget, and a least-privilege Lambda role.

```bash
# 1. Set the DB admin password (never commit it).
export TF_VAR_db_password='a-strong-password'

# 2. Deploy everything: layer build, terraform apply, widget upload.
./scripts/deploy.sh
```

Then load the dataset with `./scripts/seed_db.sh` (run from inside the VPC — the RDS instance is not publicly accessible), which creates the read-only `analytics_ro` user and switches the Secrets Manager secret to that connection string. Terraform will not revert that switch.

The demo widget shows the generated SQL, the guardrail verdict, and the results table for each question. `./scripts/demo.sh` curls the API with one valid question, one that gets blocked, and one referencing an unknown table.

The database can also be an existing Supabase Postgres instead of RDS: load `sql/retail_schema.sql` into it and point the Secrets Manager secret at it — no code or Terraform change is needed beyond that.

## Costs and honest trade-offs

Roughly $30/month while deployed in us-east-1, mostly the RDS `db.t3.micro` (~$13) and two VPC interface endpoints (~$7 each). Bedrock is pay-per-token (pennies per demo question), DynamoDB is on-demand, and API Gateway, Lambda, S3, and Secrets Manager are within or near free-tier levels at demo volume. Run `terraform destroy` when you are done.

Two things are not automated by design: enabling Bedrock model access in an account is a console action Terraform cannot do, and seeding must run from inside the VPC. And one deliberate demo trade-off: the widget is public and the API has no authorizer. The widget contains no secrets, and the worst case for an unauthenticated caller is a read-only query against the demo dataset. For a real deployment, put the widget behind CloudFront with Origin Access Control, restrict the API CORS origins, and add an authorizer.

## Why this matters

This is the interactive companion to the other two projects in this series. The compliance pipeline showed how to keep deterministic data engineering separate from probabilistic agent reasoning; the Kiro case study showed how to govern an agent that writes SQL. This layer shows the same principle from the user's side: a business user asks a question in plain English, an agent translates it, and deterministic guardrails — plus a read-only role, a read-only transaction, and a full audit log — make sure the answer can only ever come from a safe, bounded, reviewable query. That is what Analytics Using Generative AI for Business Decisions looks like when Responsible AI is built in, not bolted on.
