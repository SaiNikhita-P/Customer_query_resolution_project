# Client Query Navigator

## Overview

Client Care Navigator is a web application developed with Flask and MongoDB, designed for intelligent question answering using OpenAI embeddings. This README provides an overview of its architecture, features, and usage.

## Features

- **Question Answering**: Utilizes OpenAI embeddings to retrieve answers based on user-submitted questions.
- **Similar Question Search**: Provides suggestions for similar questions if an exact match is not found.
- **Answer Submission**: Allows users to contribute new answers for questions.
- **Persistent Storage**: MongoDB stores questions, embeddings, and answers for efficient retrieval.

## Architecture

- **Flask**: Lightweight web framework for Python, handling HTTP requests and responses.
- **MongoDB**: NoSQL database for storing and querying question-answer pairs.
- **OpenAI Embeddings**: Integration for generating and querying embeddings to enhance question similarity and retrieval.

## Project Structure

- **app.py**: Main application file, handles routing and request handling.
- **db.py**: Manages MongoDB connection and CRUD operations for questions and answers.
- **openai_embed.py**: Implements functions to generate embeddings using OpenAI's API.
- **templates/**: Directory containing HTML templates for rendering web pages.
- **static/**: Directory for static assets (e.g., CSS, JavaScript) used by the web interface.

## Usage

1. **Run the Application**:
   - Ensure Python and required packages are installed.
   - Execute `python app.py` to start the Flask web server.
   - Access the application at `http://localhost:5000` in your web browser.

2. **Using the Application**:
   - Enter a question in the provided input field on the homepage.
   - Submit the question to receive an answer.
   - If an exact match is not found, similar questions and their corresponding answers are suggested.
   - Users can contribute new answers by submitting them through the interface.

