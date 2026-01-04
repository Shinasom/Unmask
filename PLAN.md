SEC-UR Privacy - Project Plan & Roadmap
This document outlines the strategic plan, scope, and architecture for the development of the SEC-UR Privacy project.

1. Primary Goal
To develop a modern, secure, scalable, and professional full-stack application. The architecture will follow industry best practices, prioritizing robust privacy controls, secure authentication, and seamless user experience.

2. Current Status (As of January 4, 2026)
The project is well underway. The core functionality for the Phase 1 MVP has been successfully implemented and tested, and significant progress has been made on Phase 2 social features.

COMPLETED
 Backend: Secure User Authentication, Photo Management, Core Consent Workflow (Recognition, Masking, Unmasking), Admin Panel, and Real-time WebSockets.

COMPLETED
 Frontend: Component-based UI architecture (Next.js), user registration/login forms, photo upload modal, photo feed, Direct Messaging UI, and Social Interaction Components.

3. Phased Delivery Plan

Phase 1: MVP Core & Security
Goal: Establish a robust, scalable, and production-ready foundation by implementing critical performance optimizations and strict security measures.

Scope (Status of Phase 1 Tasks):

[COMPLETED] Performance Optimization (Backend):
* Pre-calculate and store face encodings on the `CustomUser` model to dramatically speed up face comparisons.
* *Implementation:* `face_encoding` JSONField added to `CustomUser`. `extract_face_encoding` service and management commands implemented.

[COMPLETED] API Security Hardening (Backend & Frontend):
* Backend: Implement strict permission controls on `UserViewSet` to prevent unauthorized listing or modification of user data.
* *Implementation:* `UserViewSet` permissions configured; custom actions (`profile`, `follow`) created with specific `IsAuthenticated` checks.

[PENDING] Configuration Management (Backend):
* Secure the `settings.py` file by moving secrets to environment variables using `python-decouple`.
* *Current Status:* Secrets and Debug mode are currently hardcoded for development.

Phase 2: Social Feature Expansion
Goal: Build upon the stable foundation by adding standard social media features to create a feature-complete application.

Scope (Status of Phase 2 Tasks):

[COMPLETED] Friend/Follower System:
* Backend: `Follow` model and endpoints (`follow`, `unfollow`, `followers`, `following`) implemented.
* Frontend: UI for managing connections and viewing network stats.

[COMPLETED] Post Engagement:
* Backend: `Like` and `Comment` models implemented in `interactions` app.
* Frontend: Engagement components integrated into the main Feed.

[COMPLETED] Direct Messaging:
* Backend: Real-time chat API implemented using Django Channels and Redis.
* *Implementation:* `Conversation` and `Message` models, `ChatConsumer` for WebSockets, and secure HTTP endpoints for history.
* Frontend: Full chat interface (`/messages`) with real-time updates and typing indicators.

[PENDING] User Interaction:
* Backend: Create API endpoints for submitting feedback and reporting posts.
* Frontend: Develop UI components for feedback forms and report buttons.

Phase 3: Proposed Deployment & Optimization (Optional)
Goal: Advanced architectural improvements for high-scale production environments. Given the scope of this as a hobby/school project, these are considered stretch goals and may not be implemented.

Scope:
* **Asynchronous Task Processing (Backend)**: Integrate Celery and Redis to move the `process_photo_for_faces` service to a background task to prevent request timeouts during heavy upload loads.

4. High-Level Architecture
The project is built on a modern, decoupled, three-part architecture:

* **Backend API**: A "headless" API built with Django and Django REST Framework.
* **Real-time Layer**: Django Channels with Redis backing for WebSocket connections (Chat).
* **Admin Panel**: Utilizes the built-in Django Admin site for secure system management.
* **User Web App**: A user-facing frontend built with Next.js that consumes the backend API.

5. Final Steps
* **Security Audit**: Rotate `SECRET_KEY`, disable `DEBUG`, and restrict `ALLOWED_HOSTS`/`CORS_ORIGINS` before final submission.
* **Cleanup**: Remove unused code and finalize `requirements.txt`.
