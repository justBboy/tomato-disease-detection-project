# Technical Architecture

## Overview

This project will be implemented as a minimal but efficient end-to-end intelligent system for tomato leaf disease analysis. The solution will combine deep learning, backend APIs, a mobile application, and a web-based admin dashboard.

The system will allow a user to upload a tomato leaf image, process it through trained models, classify the disease, segment infected regions at pixel level, estimate disease severity, and display the results through mobile and web interfaces.

For implementation details (models, backend, mobile, admin, and concepts used), see:

- [Implementation Methodology](./implementation-methodology.md)

---

## Technical Goals

The technical implementation aims to:

- Keep the system minimal and manageable for a student project
- Maintain a clean and scalable structure
- Support efficient end-to-end functionality
- Make future model integration straightforward
- Produce a working prototype that is easy to demonstrate

---

## Core System Components

The system will consist of the following major parts:

### 1. Deep Learning Layer

This is the intelligence layer of the system.

It will handle:

- Disease classification
- Pixel-level segmentation of infected regions
- Disease severity estimation

### 2. Backend API Layer

This will be built with **FastAPI**.

It will handle:

- Image upload
- Input validation
- Model inference
- Returning prediction results
- Serving data to the mobile app and admin dashboard

### 3. Mobile Client

This will be built with **React Native**.

It will allow users to:

- Upload tomato leaf images
- View disease prediction results
- View segmentation output
- View disease severity result

### 4. Admin Dashboard

This will be built with **Next.js**.

It will allow administrators or project reviewers to:

- Test the system through image upload
- View prediction results
- Monitor prediction history
- Interact with a more detailed system interface

---

## Proposed High-Level Architecture

```text
React Native Mobile App
        |
        v
     FastAPI Backend
        |
        v
 Deep Learning Inference Layer
        |
        v
 Classification + Segmentation Output
        |
        v
 Next.js Admin Dashboard
```
