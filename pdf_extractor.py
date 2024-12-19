import streamlit as st
import fitz  # PyMuPDF for PDF processing
import re
import openai
from dotenv import load_dotenv
import os

load_dotenv()

# Read the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")


def extract_questions(pdf_path):
    """
    Extract questions from even pages of a PDF starting from page 2.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        list: List of questions extracted from the PDF.
    """
    def extract_text_from_pdf(pdf_path):
        text = ""
        pdf_document = fitz.open(pdf_path)
        for page_number in range(len(pdf_document)):
            # Process only even pages (1-indexed), skipping the first page
            if page_number == 0:
                continue
            if (page_number) % 2 == 0:
                page = pdf_document[page_number]
                text += page.get_text("text") + "\n"
        pdf_document.close()
        return text

    def parse_questions(text):
        question_pattern = r"(\d+\..*?)(?=\d+\.|\Z)"
        questions = re.findall(question_pattern, text, re.DOTALL)
        return [q.strip() for q in questions]

    pdf_text = extract_text_from_pdf(pdf_path)
    questions = parse_questions(pdf_text)
    return questions


def generate_similar_questions(question, num_questions=10):
    """
    Use ChatGPT to generate similar questions.
    Args:
        question (str): Input question.
        num_questions (int): Number of similar questions to generate.
    Returns:
        list: List of similar questions.
    """
    prompt = (
        f"Generate {num_questions} questions similar to the following:\n\n"
        f"Original Question: {question}\n\n"
        f"Similar Questions:"
    )

    try:
        # Create a prompt message for OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.7,  # You can adjust this for more creative responses
            messages=[
                {"role": "system", "content": "You are an AI Tutor which generates similar questions based upon the topic of the question."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the generated text from the response
        generated_text = response['choices'][0]['message']['content']

        # Split the generated text into individual questions (by newline)
        similar_questions = [q.strip() for q in generated_text.split("\n") if q.strip()]
        return similar_questions

    except Exception as e:
        st.error(f"Error generating similar questions: {e}")
        return []


def check_question_quality(question):
    """
    Check the grammar and completeness of the question.
    Args:
        question (str): The question to be checked.
    Returns:
        str: Feedback from OpenAI regarding grammar or missing parts.
    """
    prompt = (
        f"Please check the following question for grammatical issues, clarity, or anything missing:\n\n"
        f"Question: {question}\n\n"
        f"Provide any suggestions or corrections for improving the question."
    )

    try:
        # Create a prompt message for OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            messages=[
                {"role": "system", "content": "You are an AI that checks questions for grammatical mistakes and completeness."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the feedback from the response
        feedback = response['choices'][0]['message']['content']
        return feedback

    except Exception as e:
        st.error(f"Error checking question quality: {e}")
        return "Error checking question quality."


# Streamlit App
st.title("PDF Question Viewer and Similar Question Generator")
st.markdown("Upload a PDF and browse questions. Generate similar questions using ChatGPT.")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    # Save the uploaded file temporarily
    with open("uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract questions from the uploaded PDF
    questions = extract_questions("uploaded_file.pdf")
    if not questions:
        st.error("No questions found in the PDF. Please upload a valid question paper.")
    else:
        # Pagination for questions
        total_questions = len(questions)
        page_number = st.number_input(
            "Question Page", min_value=1, max_value=total_questions, value=1, step=1
        )
        st.write(f"Question {page_number}:")
        current_question = questions[page_number - 1]
        st.markdown(f"**{current_question}**")

        # Check grammar and completeness of the current question
        if st.button("Check Question Quality"):
            with st.spinner("Checking question quality..."):
                feedback = check_question_quality(current_question)
                st.write("### Feedback on Question Quality:")
                st.markdown(f"{feedback}")

        # Generate similar questions
        if st.button("Generate Similar Questions"):
            with st.spinner("Generating similar questions..."):
                similar_questions = generate_similar_questions(current_question)
                if similar_questions:
                    st.write("### Similar Questions:")
                    for i, sq in enumerate(similar_questions, 1):
                        st.markdown(f"{sq}")
                else:
                    st.error("Failed to generate similar questions.")
