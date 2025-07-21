---
title: Boosting Data Performance: Indexing, Partitioning & Compression Explained with Examples
author: Krishna Chapagain
date: 2025-07-21
summary: In this post, we explore the foundational performance optimization techniques in databases—Indexing, Partitioning, and Compression—using practical examples and use cases.
slug: database-optimization-techniques
---

# Boosting Data Performance: Indexing, Partitioning & Compression Explained with Examples

Modern data systems handle massive volumes of information. To keep querying fast and storage efficient, three major techniques are essential: **Indexing**, **Partitioning**, and **Compression**. Let’s break them down with examples.

---

## 🔍 Indexing in Databases

### What is Indexing?

Indexing is a data structure technique used to optimize the retrieval speed of records from a database table. It works like a **book index**, pointing directly to the rows where data resides.

### Common Attributes of Indexing

| Attribute           | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| **Type**            | B-tree, Hash, Bitmap, Full-text, GiST, etc.                                 |
| **Column(s)**       | Index can be created on one or more columns.                                |
| **Uniqueness**      | UNIQUE indexes prevent duplicate values in the column.                      |
| **Order**           | Can be ASC or DESC depending on use-case (e.g., range scans).               |
| **Include Columns** | In some DBMS (like SQL Server), you can include extra columns in the index. |
| **Access Type**     | How data is accessed (sequential scan, index scan, bitmap scan).            |
| **Access Time**     | Time taken to retrieve data using the index.                                |
| **Insertion Time**  | Time taken to insert a record into the indexed table.                       |
| **Deletion Time**   | Time required to delete a record and maintain index consistency.            |
| **Space Overhead**  | Additional storage needed to maintain the index structure.                  |

### Example (PostgreSQL)

```sql
-- Creating a B-tree index on customer_id
CREATE INDEX idx_customer_id ON orders (customer_id);

-- Creating a multi-column index
CREATE INDEX idx_order_date_status ON orders (order_date, status);
```

### Use Case

- Fast lookups of orders by `customer_id`.
- Efficient filtering when both `order_date` and `status` are in the WHERE clause.

---

## 🧩 Partitioning

### What is Partitioning?

Partitioning splits a large table into **smaller, manageable chunks** (partitions) based on specific column values like date, region, or ID range. It improves query performance and maintenance.

### Types of Partitioning

| Type            | Description                                                    | Example                                  |
|------------------|----------------------------------------------------------------|-------------------------------------------|
| **Range**        | Partitions by value range.                                    | Dates, e.g., Jan to Mar, Apr to Jun       |
| **List**         | Partitions by specific values.                                | Region = 'APAC', 'EMEA'                   |
| **Hash**         | Distributes rows using a hash function.                       | Used when data distribution is random     |
| **Composite**    | Combines two or more partition types.                         | Range + Hash                              |

### Example (PostgreSQL)

```sql
-- Creating a range partitioned table on order_date
CREATE TABLE orders (
    order_id INT,
    order_date DATE,
    customer_id INT,
    ...
) PARTITION BY RANGE (order_date);

-- Creating child partitions
CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
```

### Benefits

- **Faster queries** on partition-pruned data.
- Easier **archiving and purging** of old data.
- Parallel query execution on partitions.

---

## 📦 Compression Techniques

### Why Compress Data?

Compression reduces storage usage and can **speed up IO-bound queries** by reading less from disk.

### Types of Compression

| Type              | Description                                                           | Suitable For                     |
|-------------------|-----------------------------------------------------------------------|----------------------------------|
| **Row-level**     | Compresses individual rows.                                           | OLTP systems                     |
| **Page-level**    | Compresses data pages in memory or disk.                             | SQL Server, PostgreSQL           |
| **Columnar**      | Compresses column-wise, effective when data in columns is repetitive. | Data Warehouses (Redshift, BigQuery) |
| **Dictionary**    | Stores repetitive strings once and uses a pointer.                   | String-heavy columns             |

### Example (Amazon Redshift)

```sql
-- Creating a table with columnar compression
CREATE TABLE sales (
    sale_id INT,
    product_id INT ENCODE AZ64,
    sale_date DATE ENCODE ZSTD,
    region VARCHAR(50) ENCODE TEXT255
);
```

> `ENCODE` defines the compression type per column.

### Compression Techniques in Action

| DB System        | Feature Name            | Compression Type      |
|------------------|-------------------------|------------------------|
| PostgreSQL       | TOAST                   | Page-level             |
| Amazon Redshift  | ENCODE                  | Column-level           |
| SQL Server       | ROW/PAGE compression    | Row/Page-level         |
| Snowflake        | Automatic (Transparent) | Hybrid/Columnar        |

---

## ✅ Final Thoughts

- Use **indexes** to boost read performance on frequent filter or join columns.
- **Partition** your tables when dealing with time-series, regional, or large datasets.
- Apply **compression** to save cost and enhance IO efficiency—especially in data lakes or warehouses.

> ⚡ Optimization is **context-specific**—test, measure, and tune based on your workload and infrastructure.

---

## 💬 Got Questions?

**🗨️ Connect with me on [LinkedIn](https://www.linkedin.com/in/krishna-prasad-chapagain/)** | **Check out my other posts on [Datalytics](http://www.datalytics.me/blog)**

---

## 📌 Tags

`#DataEngineering` `#PostgreSQL` `#Indexing` `#Partitioning` `#DataCompression` `#AWSRedshift` `#DatabaseOptimization`
