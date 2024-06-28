## Overview

Redhat Panda's LLM Pen Testing Solution is a security testing tool designed to identify and address potential security risks in web applications. 
It enhances the overall security of your application by detecting exposed API routes and keys, identifying Personally Identifiable Information (PII), among other features.

## Key Features

- **Transparent Pricing for All**: Unlike current solutions that focus on enterprise-level needs with non-transparent pricing, Redhat Panda ensures that hobby projects and startups also have access to affordable security solutions.
- **Easy Integration and Comprehensive Security Checks**: The solution can be effortlessly integrated into your deployment pipeline. It provides concise yet comprehensive security checks, ensuring that no project is left unprotected.

## Tech Stack

The technology stack used for this solution includes:

- **Frontend**: Streamlit Python
- **Backend**: Serverless FastAPI hosted through Modal, Playwright for headless web traffic, and Redis: KV for synchronizing published events in a distributed system.
- **Infrastructure**: Modal for autoscaling serverless cloud compute, Upstash Redis for serverless redis instance.
- **LLMs**: Anthropic’s Claude 3 Haiku through AWS for in-depth network analysis, OpenAI’s gpt-4o for user audit summarization.
