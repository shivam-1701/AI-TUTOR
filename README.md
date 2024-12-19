# PDF Question Viewer and Similar Question Generator

## Overview
This Streamlit application allows users to upload a PDF containing questions, extract the questions from even pages (starting from page 2), and generate similar questions using OpenAI's GPT-3.5 model. The app is designed for easy browsing and question generation based on the input document.

## Features
- **Upload a PDF**: Users can upload a PDF file containing questions.
- **Extract Questions**: The app extracts questions from even pages of the PDF.
- **Generate Similar Questions**: Using OpenAI's GPT-3.5, the app generates similar questions based on the input question.

## Installation

To run this project locally, follow these steps:

### 1. Clone the Repository (if applicable)
If this is a GitHub repository, you can clone it using the following command:
```bash
git clone https://github.com/shivam-1701/AI-TUTOR.git
streamlit run pdf_extractor.py