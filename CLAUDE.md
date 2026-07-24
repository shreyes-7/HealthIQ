# CLAUDE.md

# Healthcare AI Engineering Guide

Version: 1.0

---

# Purpose

This repository contains a production-grade AI-powered healthcare application for predicting Emergency Department admissions using the NHAMCS dataset.

Always prioritize:

- Correctness
- Maintainability
- Readability
- Scalability
- Simplicity

Do not optimize prematurely.

Never sacrifice architecture for short-term convenience.

Always assume this project will continue growing.

---

# Primary Goal

Build a professional healthcare AI platform.

The project should feel like software developed by an experienced engineering team rather than a college assignment.

The application should be:

- Modular
- Reusable
- Extensible
- Production Ready

---

# Project Architecture

The repository is divided into independent systems.

Frontend

Backend

Machine Learning

Documentation

Each system has a single responsibility.

Never mix responsibilities.

---

# Separation of Concerns

Machine Learning

Responsible for:

- preprocessing

- training

- evaluation

- explainability

Backend

Responsible for:

- APIs

- validation

- inference

- database

Frontend

Responsible for:

- UI

- visualization

- API communication

Never violate these boundaries.

---

# Development Environment

When setting up the project for the first time:

- Create a Python virtual environment named `.venv` in the repository root.
- Never install packages globally.
- Activate the virtual environment before installing dependencies.
- Maintain `requirements.txt` for runtime dependencies.
- Maintain `requirements-dev.txt` for development tools.
- Keep dependencies minimal and remove unused packages.


---


# General Principles

Always prefer

Simple code

Readable code

Reusable code

Documented code

Predictable code

Avoid

God classes

Massive files

Duplicate logic

Magic numbers

Hardcoded configuration

Premature optimization

---

# Coding Standards

Write code that another developer can understand six months later.

Use meaningful names.

Avoid abbreviations.

Keep functions focused.

Keep files organized.

Avoid nested logic when possible.

Prefer early returns.

---

# Function Guidelines

Functions should:

Perform one task.

Be easy to test.

Have descriptive names.

Avoid side effects.

Return predictable outputs.

Break large functions into smaller reusable functions.

---

# File Organization

Each file should have one primary purpose.

Examples

prediction_service.py

Only prediction logic.

database.py

Only database configuration.

router.py

Only API routes.

Avoid placing unrelated code inside a single file.

---

# Configuration

Never hardcode:

API keys

Passwords

Database URLs

Secrets

Tokens

Always use environment variables.

---

# Error Handling

Never silently ignore errors.

Return meaningful exceptions.

Log failures.

Validate inputs.

Provide useful messages.

Avoid exposing internal implementation details.

---

# Logging

Log important events.

Examples:

Application startup

Prediction request

Model loading

Unexpected failures

Avoid excessive logging.

Never log sensitive information.

---

# Database

Database logic belongs inside the data layer.

Avoid SQL inside API routes.

Keep transactions short.

Use migrations.

Use models consistently.

---

# Backend

Business logic should never exist inside route handlers.

Routes should:

Receive request.

Validate request.

Call service.

Return response.

Nothing more.

---

# API Design

REST principles should be followed.

Endpoints should:

Have one responsibility.

Use proper HTTP methods.

Return structured JSON.

Return appropriate status codes.

Version APIs.

Document APIs.

---

# Validation

Validate everything.

Never trust client input.

Reject malformed requests.

Reject missing required fields.

Reject invalid values.

---

# Machine Learning

Training code should never exist inside the backend.

Inference code should never retrain models.

Model artifacts should be loaded only once whenever possible.

Preprocessing during inference must exactly match preprocessing during training.

---

# Explainable AI

Every prediction must include an explanation.

Explainability is a required feature.

Not an optional enhancement.

---

# Frontend

Business logic belongs in the backend.

Frontend responsibilities:

Display information.

Collect user input.

Visualize results.

Communicate with APIs.

Nothing more.

---

# React Guidelines

Prefer functional components.

Prefer reusable components.

Keep components small.

Extract repeated UI.

Avoid deeply nested components.

---

# State Management

Keep state minimal.

Separate

Server state

UI state

Form state

Avoid duplicated state.

---

# Styling

Maintain a professional healthcare appearance.

Avoid inconsistent spacing.

Use consistent typography.

Use reusable design patterns.

Prioritize accessibility.

---

# Documentation

Document:

Complex functions.

Public APIs.

Architecture decisions.

Non-obvious implementations.

Do not document obvious code.

---

# Git Workflow

Work on feature branches.

Keep commits focused.

Write meaningful commit messages.

Avoid committing unfinished work to main.

---

# Commit Message Format

Examples

feat: add prediction endpoint

fix: resolve validation bug

docs: update architecture

refactor: simplify preprocessing

test: add API tests

---

# Pull Requests

Every PR should:

Compile successfully.

Pass tests.

Follow coding standards.

Avoid unnecessary changes.

Update documentation if required.

---

# Testing

Every feature should be testable.

Prefer automated testing.

Test:

Validation

Prediction

Database

Utilities

API endpoints

Frontend components

---

# Performance

Optimize only after correctness.

Avoid unnecessary computation.

Reuse expensive resources.

Lazy load where appropriate.

Cache only when beneficial.

---

# Security

Never expose:

Secrets

Internal paths

Stack traces

Database credentials

Validate every external input.

---

# Dependency Management

Avoid unnecessary dependencies.

Prefer mature libraries.

Keep dependencies updated.

Remove unused packages.

---

# Code Quality

Before writing code ask:

Is it readable?

Is it reusable?

Is it testable?

Is it modular?

Can it be simplified?

If yes, simplify it.

---

# Refactoring

Improve code when necessary.

Do not refactor unrelated modules.

Preserve behavior.

Reduce duplication.

Increase readability.

---

# AI Assistance

When generating code:

Prefer maintainability over cleverness.

Avoid placeholder implementations.

Generate production-quality code.

Follow existing project architecture.

Reuse existing utilities whenever appropriate.

Never duplicate existing functionality.

Search the repository before creating new modules.

---

# Decision Making

When multiple implementation choices exist:

Prefer

Readability

Scalability

Maintainability

Industry best practices

Explain important architectural decisions.

---

# When Unsure

Do not guess.

Inspect the repository.

Reuse existing patterns.

Ask for clarification only when requirements are genuinely ambiguous.

---

# Definition of Done

A feature is complete when:

✓ Code compiles.

✓ Tests pass.

✓ Documentation updated.

✓ No duplicated logic.

✓ Error handling implemented.

✓ Logging added where appropriate.

✓ Code reviewed.

✓ Follows architecture.

✓ Ready for production.

---

# Final Instruction

Every contribution should improve the repository.

Do not merely make the code work.

Make the code understandable, maintainable, scalable, and production-ready.