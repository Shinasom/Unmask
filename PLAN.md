# 🛡️ SEC-UR Privacy — Project Plan & Roadmap

**Status:** 🟢 Active Development  
**Last Updated:** January 4, 2026

---

## 1. 🎯 Primary Goal
To develop a modern, secure, scalable, and professional full-stack application. The architecture follows industry best practices, prioritizing robust privacy controls, secure authentication, and a seamless user experience.

---

## 2. 📊 Current Status
The project is well underway. The core functionality for the **Phase 1 MVP** has been successfully implemented and tested, and significant progress has been made on **Phase 2** social features.

### ✅ Completed Milestones
* **Backend:** Secure User Authentication, Photo Management, Core Consent Workflow (Recognition, Masking, Unmasking), Admin Panel, and Real-time WebSockets.
* **Frontend:** Component-based UI architecture (Next.js), User Registration/Login forms, Photo Upload Modal, Photo Feed, Direct Messaging UI, and Social Interaction Components.

---

## 3. 🚀 Phased Delivery Plan

### 🔹 Phase 1: MVP Core & Security
**Goal:** Establish a robust, scalable, and production-ready foundation by implementing critical performance optimizations and strict security measures.

#### Tasks & Progress
- [ ] **Asynchronous Task Processing (Backend)**
    - *Objective:* Integrate Celery and Redis to move the `process_photo_for_faces` service to a background task.
    - *Note:* Redis is currently installed for Channels, but Celery is not yet integrated.

- [x] **Performance Optimization (Backend)**
    - *Objective:* Pre-calculate and store face encodings on the `CustomUser` model to dramatically speed up face comparisons.
    - *Implementation:* Added `face_encoding` JSONField to `CustomUser`. Implemented `extract_face_encoding` service and management commands.

- [x] **API Security Hardening (Backend & Frontend)**
    - *Objective:* Implement strict permission controls on `UserViewSet` to prevent unauthorized listing or modification of user data.
    - *Implementation:* Refactored `UserViewSet` permissions; created custom actions (`profile`, `follow`) with specific `IsAuthenticated` checks.

- [ ] **Configuration Management (Backend)**
    - *Objective:* Secure the `settings.py` file by moving secrets to environment variables using `python-decouple`.
    - *Status:* Secrets and Debug mode are currently hardcoded for development.

### 🔹 Phase 2: Social Feature Expansion
**Goal:** Build upon the stable foundation by adding standard social media features to create a feature-complete application.

#### Tasks & Progress
- [x] **Friend/Follower System**
    - *Backend:* Implemented `Follow` model and endpoints (`follow`, `unfollow`, `followers`, `following`).
    - *Frontend:* Built UI for managing connections and viewing network stats.

- [x] **Post Engagement**
    - *Backend:* Implemented `Like` and `Comment` models in the `interactions` app.
    - *Frontend:* Integrated engagement components into the main Feed.

- [x] **Direct Messaging**
    - *Backend:* Implemented real-time chat API using **Django Channels** and **Redis**.
    - *Implementation:* Created `Conversation` and `Message` models, `ChatConsumer` for WebSockets, and secure HTTP endpoints for history.
    - *Frontend:* Built full chat interface (`/messages`) with real-time updates and typing indicators.

- [ ] **User Interaction**
    - *Backend:* Create API endpoints for submitting feedback and reporting posts.
    - *Frontend:* Develop UI components for feedback forms and report buttons.

---

## 4. 🏗️ High-Level Architecture
The project is built on a modern, decoupled, three-part architecture:

1.  **Backend API:** A "headless" API built with **Django** and **Django REST Framework**.
2.  **Real-time Layer:** **Django Channels** with **Redis** backing for WebSocket connections (Chat).
3.  **Admin Panel:** Utilizes the built-in Django Admin site for secure system management.
4.  **User Web App:** A user-facing frontend built with **Next.js** that consumes the backend API.

---

## 5. 🏁 Final Steps
Before the final submission, the following housekeeping tasks must be performed:

- [ ] **Security Audit:**
    - Rotate `SECRET_KEY`.
    - Disable `DEBUG`.
    - Restrict `ALLOWED_HOSTS` and `CORS_ORIGINS`.
- [ ] **Cleanup:** Remove unused code and finalize `requirements.txt`.
