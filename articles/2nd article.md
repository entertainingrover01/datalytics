title: Understanding SCD Type 1 and Type 2 in Data Warehousing
author: Krishna Chapagain
date: 2025-06-21
summary: A beginner-friendly introduction to Slowly Changing Dimensions (SCD) Types 1 and 2—what they are, when to use them, and how they impact your data architecture.
slug: scd-type-1-vs-type-2

Understanding SCD Type 1 and Type 2 in Data Warehousing

When working with dimensional data models, particularly in data warehouses or BI systems, handling changes to dimension data over time is a common and critical challenge. This is where Slowly Changing Dimensions (SCD) come in.

What are Slowly Changing Dimensions (SCD)?

In a star schema or snowflake schema, dimension tables store descriptive attributes (like customer name, address, or product category) that can change over time. But how do we manage these changes while preserving the historical context of facts?

SCD is a set of techniques used to handle these changes. Today, we’ll focus on the two most widely used types: SCD Type 1 and SCD Type 2.

🔄 SCD Type 1: Overwrite the Past

Definition:
SCD Type 1 simply updates the existing dimension record with new data. There’s no history preserved.

When to use:

When maintaining historical data isn’t important.
For correcting errors (e.g., a typo in a customer's name).
When the change should apply retroactively in all reports.
Example:

CustomerID	Name	City
101	John Doe	New York
If John moves to Chicago:

CustomerID	Name	City
101	John Doe	Chicago
Pros:

Simple to implement.
No data bloat.
Cons:

Loss of historical information.
📘 SCD Type 2: Preserve History

Definition:
SCD Type 2 adds a new row for every change in the dimension attribute, thus preserving the full history.

When to use:

When historical reporting is essential.
To track how dimension values changed over time.
Implementation typically includes:

Surrogate key (e.g., CustomerSK)
Start and end dates
Current flag (IsCurrent)
Example:

CustomerSK	CustomerID	Name	City	StartDate	EndDate	IsCurrent
1	101	John Doe	New York	2022-01-01	2023-06-15	N
2	101	John Doe	Chicago	2023-06-16	NULL	Y
Pros:

Preserves full history.
Enables point-in-time analysis.
Cons:

More complex queries.
Larger data size.
🔍 Choosing Between Type 1 and Type 2

Criteria	Type 1	Type 2
Historical tracking	❌ No	✅ Yes
Simplicity	✅ Simple	❌ Complex
Space requirement	✅ Low	❌ Higher
Use case	Corrections only	Historical analysis

Posted on June 21, 2025
