import re
import pandas as pd
import fitz  # PyMuPDF


def extract_questions_and_options(pdf_path):
    """
    Extract questions and options (including math symbols and fractions)
    from alternate pages of a PDF file, ignoring the first page.

    Args:
        pdf_path (str): Path to the question paper PDF.

    Returns:
        pd.DataFrame: DataFrame containing English questions and their options.
    """

    def extract_text_from_even_pages(pdf_path):
        """
        Extract text content from even pages of the PDF.
        """
        text = ""
        pdf_document = fitz.open(pdf_path)

        for page_number in range(1, len(pdf_document)):
            if page_number % 2 == 0:  # Even pages only, excluding first page
                page = pdf_document[page_number]
                text += page.get_text("text") + "\n"

        pdf_document.close()
        return text

    def filter_text(text):
        """
        Remove non-Latin scripts but keep math symbols, fractions, and special characters.
        """
        filtered_text = re.sub(r'[^\w\s.,;:!?()"\'=+\-*/^√∞λμΩ∆Σπ<>≤≥≠∑∂°%&|~\[\]{}²³¼½¾√]', '', text)
        filtered_text = re.sub(r'\s+', ' ', filtered_text)  # Normalize spaces
        return filtered_text.strip()

    def parse_questions(text):
        """
        Parse questions and options from the filtered text.
        Handles questions without options as well.
        """
        # Regex pattern to match questions with or without options
        question_pattern = (
            r"(\d+\..*?)(?:(\(A\)\s.*?))?"
            r"(?:(\(B\)\s.*?))?"
            r"(?:(\(C\)\s.*?))?"
            r"(?:(\(D\)\s.*?))?"
            r"(?=\d+\.|\Z)"
        )

        matches = re.findall(question_pattern, text, re.DOTALL)
        print(f"Total matches found: {len(matches)}")  # Debugging count of questions

        question_data = []
        for match in matches:
            question = match[0].strip()
            option_a = match[1].strip() if match[1] else None
            option_b = match[2].strip() if match[2] else None
            option_c = match[3].strip() if match[3] else None
            option_d = match[4].strip() if match[4] else None

            question_data.append({
                "Question": question,
                "Option A": option_a,
                "Option B": option_b,
                "Option C": option_c,
                "Option D": option_d
            })

        return question_data

    print("Extracting text from even pages of the PDF...")
    text = extract_text_from_even_pages(pdf_path)
    print("Raw extracted text:")
    print(text[:1000])  # Print the first 1000 characters for a preview

    print("Filtering text to retain relevant characters...")
    filtered_text = filter_text(text)

    print("Parsing questions and options...")
    question_data = parse_questions(filtered_text)

    if not question_data:
        print("No questions or options found. Check PDF structure or regex.")
        return pd.DataFrame()  # Return empty DataFrame if no data found

    df = pd.DataFrame(question_data)
    return df


# Example usage
pdf_file = "/home/shivam/PycharmProjects/AI_TUTOR/question_paper/PHYSICS/55_1_2_Physics.pdf"  # Replace with your path
df_questions = extract_questions_and_options(pdf_file)

if not df_questions.empty:
    # Save to CSV
    df_questions.to_csv("extracted_questions.csv", index=False)
    print("Extracted Questions and Options:")
    print(df_questions)
else:
    print("No data extracted. Please review the PDF structure.")
