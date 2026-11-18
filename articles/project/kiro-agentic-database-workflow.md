---
title: Standardizing Agentic Workflows for Relational Data: Governing AWS Kiro with a Deterministic SQL Validator
author: Krishna Prasad Chapagain
date: 2026-11-18
summary: A governed workflow for letting an AI coding agent (AWS Kiro) generate SQL and database schemas without breaking production rules — Kiro specs and steering docs teach the agent the rules, and a deterministic validator proves it followed them before a human ever sees the SQL.
slug: kiro-agentic-database-workflow
tags: ["Data Engineering", "Agentic AI", "AWS", "Kiro", "Terraform", "PostgreSQL", "Responsible AI"]
repo: https://github.com/entertainingrover01/aws-kiro-agentic-database-workflow
---

# Standardizing Agentic Workflows for Relational Data: Governing AWS Kiro with a Deterministic SQL Validator

AI coding agents are good at drafting SQL and bad at knowing what they are not allowed to do. Left ungoverned, an agent will join on a column that does not exist because it looks plausible, return a DELETE for a read request, copy a DROP TABLE out of an example, or `SELECT *` over a wide table and return columns nobody asked for.

In a regulated environment, any one of those is a failed control. This project is the control: a deterministic validator between the agent and the database, plus the Kiro specs and steering docs that teach the agent the rules in the first place.

You can explore the complete repository on GitHub: [aws-kiro-agentic-database-workflow](https://github.com/entertainingrover01/aws-kiro-agentic-database-workflow).

## Before / after

**Before** — agent SQL goes straight to the database. The user prompts, Kiro generates SQL, it runs against PostgreSQL, and the user gets a result or a runtime error. Nothing checks whether the statement was safe, in scope, or even against a real schema.

**After** — the validator sits between the agent and the database. Kiro drafts SQL, the validator checks it against the schema and the guardrail rule set, failures go back to the agent with the violations named, and only passing SQL reaches a human reviewer. Approved SQL is then handed to the database — nothing here runs agent-generated SQL unattended.

```flowchart
flowchart LR
    U[User prompt] --> K[Kiro agent]
    K -->|drafts SQL| V[Validator: mode + schema + guardrails]
    S[Schema JSON] --> V
    V -->|FAIL + violations| K
    V -->|PASS| R[Human review]
    R -->|approved| D[(RDS PostgreSQL)]
```

The same validator code runs in two places: as a local CLI and as an AWS Lambda (`sql-guardrail-validator`) that loads the schema from S3. One rule set, two runtimes, no drift between what you test locally and what runs in the cloud.

## The specs and guardrails the agent works under

The `.kiro/` directory is the other half of the project — it is how the agent learns the rules before it writes anything:

- `.kiro/specs/agentic-db-workflow/requirements.md` — requirements with acceptance criteria.
- `.kiro/specs/agentic-db-workflow/design.md` — architecture, the validation pipeline, and the design decisions.
- `.kiro/specs/agentic-db-workflow/tasks.md` — the implementation checklist, marked done.
- `.kiro/steering/sql-standards.md` — SQL style rules the agent must follow.
- `.kiro/steering/guardrails.md` — the guardrail contract: validate before showing SQL, never route around the validator.

The steering docs tell the agent what to do; the validator proves it did it. Neither replaces the human reviewer.

The guardrail rules themselves are deterministic and stdlib-only:

| Rule | What it does |
|---|---|
| Mode allowlist | `read` = SELECT/WITH only; `ddl` = CREATE/ALTER only; `write` = INSERT/UPDATE/DELETE only |
| Single statement | Stacked queries rejected |
| Comment hygiene | Comments containing SQL keywords rejected (no smuggling) |
| Schema validation | Every table and column must exist in the schema file |
| System catalogs | `information_schema` / `pg_catalog` always blocked |
| Projection width | `SELECT *` rejected unless explicitly allowed |
| Scoped writes | DELETE / UPDATE require a WHERE clause, in every mode |
| DDL path | Additive only (CREATE TABLE / INDEX, ADD COLUMN, RENAME); DROP always blocked |

The single source of truth is `schema/retail_schema.json` — customers, orders, order_items, products, inventory — with the same schema as Postgres DDL plus seed rows in `sql/demo_schema.sql`.

## Failure modes caught

These are not hypothetical. Every row is exercised by the demo script and by the unit tests, with a good/bad example file in the repo for each one:

| Failure mode | What the agent produced |
|---|---|
| Hallucinated join | A JOIN on a column that does not exist (`o.shipping_address`) |
| Hallucinated table | A query against a table that is not in the schema (`shipments`) |
| Unsafe DDL | `DROP TABLE` presented as part of a read task |
| Unscoped DELETE | `DELETE FROM orders` with no WHERE |
| Write as read | An UPDATE returned for a read request |
| Catalog probe | UNION against `information_schema` to enumerate tables |
| SELECT * over wide tables | Unbounded projection |
| Stacked query | A read followed by a DELETE in one submission |
| Comment smuggling | Keywords hidden in a `/* */` comment to slip past a naive filter |
| Destructive DDL | `ALTER TABLE ... DROP COLUMN` (data loss) |
| Schema drift | DDL referencing a table that does not exist, or adding a column that already exists |

What these have in common: the first group is the agent guessing at the schema, the second is the agent producing a more powerful statement than the task asked for, and the rest are shape problems — too wide, too many, too sneaky. The validator treats all of them the same way: a deterministic check against the schema file and the rule set, with the violation named in the output.

## CLI automation

The validator and the demo run entirely locally with Python 3.10+ and no dependencies — no AWS needed to try it:

```bash
# Run the tests (63 tests, stdlib unittest)
python3 -m unittest discover -s tests -v

# Validate one file
python3 src/guardrails/validate_sql.py sql/examples/good/low_stock.sql
python3 src/guardrails/validate_sql.py --mode ddl sql/examples/ddl/good_add_column.sql

# Run the end-to-end demo: validator report over all examples,
# plus an EXPLAIN dry-run if a database is reachable
./scripts/run_workflow.sh
```

`run_workflow.sh` prints a pass/fail report (18 checks: 3 good, 10 bad, 3 DDL, 2 write-mode) and exits non-zero if any expectation fails.

## Deploy to AWS

Terraform provisions a private-only VPC (10.0.0.0/16, two AZs, no internet gateway), one RDS PostgreSQL 15 instance (`db.t3.micro`, single-AZ, 20 GB gp3, storage-encrypted, private to the VPC), a versioned, encrypted S3 artifacts bucket holding the schema JSON, and a Python 3.12 Lambda running the same validator code as the CLI, with a least-privilege IAM role (CloudWatch logs + read access to the schema object only — no database access).

```bash
cd terraform
terraform init
terraform apply -var="db_password=<redacted>"
```

A passing query invoked on the deployed Lambda returns HTTP 200 with `valid: true`; a failing one returns 400 with the violation list. Cleanup is `terraform destroy`.

## What the validator does not catch

Honest scope matters here. The validator proves SQL is safe to run, not that it is right:

- A query that is valid SQL against real columns but answers the wrong question (wrong join, wrong filter, wrong aggregation).
- A query that is valid but slow (no EXPLAIN cost check in the validator; the demo's EXPLAIN dry-run is a human eyeball check).
- Data-dependent problems (a WHERE clause that matches zero rows, or every row).
- CTE and subquery output columns, which cannot be inferred statically.

These are human-review problems, and the workflow keeps a human in the loop for exactly that reason.

## Why this matters for enterprise data teams

This is the same boundary I drew in the agentic compliance pipeline: separate what must be deterministic from what can be probabilistic. The agent is free to be creative about *how* to answer a question; it is not free to decide *what it is allowed to touch*. The specs teach it the rules, the validator enforces them, and a human still signs off before anything runs. That is how agentic coding tools become governable in a structured enterprise environment — not by trusting the model more, but by checking it deterministically.
