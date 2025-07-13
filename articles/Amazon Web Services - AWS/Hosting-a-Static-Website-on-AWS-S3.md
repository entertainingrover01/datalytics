---
title: Hosting a Static Website on AWS S3 My Experience and Guide
author: Krishna Prasad Chapagain
date: 2025-07-13
summary: A practical walkthrough of how I hosted my static website on Amazon S3, with pros, cons, and clear step-by-step instructions you can follow.
slug: hosting-static-website-aws-s3
---

# Hosting a Static Website on AWS S3

Recently, I set out to host my own static website using **Amazon S3** (Simple Storage Service). I followed a helpful guide from [Nextwork](https://learn.nextwork.org/projects/aws-host-a-website-on-s3?track=no) and decided to document what I learned, the steps I took, and the pros and cons you should know before trying it yourself.

---

## Why Host a Website on S3?

Amazon S3 is an easy, affordable way to host static websites — sites built with HTML, CSS, and JavaScript that don’t need a backend server. It’s perfect for portfolios, resumes, documentation, or simple landing pages.

---

## Pros

* **Low Cost:** You pay only for what you use — storage and bandwidth.
* **High Availability:** Backed by AWS’s durable infrastructure.
* **Scalable:** Automatically handles spikes in traffic.
* **Simple to Deploy:** Just upload your files.
* **Global Reach:** Works well with CloudFront CDN for faster global delivery.

---

## Cons

* **Static Only:** No server-side scripting (PHP, Node.js, etc.).
* **No HTTPS by Default:** Requires CloudFront and ACM for SSL/TLS.
* **Limited Routing:** Custom error pages and redirects can be basic.
* **Vendor Lock-In:** Ties you to the AWS ecosystem.

---

## Steps to Host a Website on S3

Here’s a simple version of the steps I followed:

### 1. Create an S3 Bucket

* Open the AWS S3 console.
* Create a bucket named exactly like your domain (e.g., `www.example.com`).
* Choose the AWS region closest to your users.

---

### 2. Upload Website Files

* Upload all your static files: `index.html`, `style.css`, `script.js`, images, etc.
* Keep your folder structure tidy.

---

### 3. Enable Static Website Hosting

* In the bucket **Properties**, enable **Static website hosting**.
* Set the index document (e.g., `index.html`) and an error document if needed.

---

### 4. Make the Bucket Public

By default, S3 blocks public access. You’ll need to add a **Bucket Policy** to allow public read access.

Example policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::www.example.com/*"
    }
  ]
}
