# from langchain_community.document_loaders import PyPDFLoader
import io
import pypdf



#to load pdf
def extractTextFromPDF(pdf_byte: bytes) ->str:

    pdf_stream = io.BytesIO(pdf_byte)

    reader = pypdf.PdfReader(pdf_stream)

    extracted_text = ""
    # Loop through pages and extract text
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
            
    return extracted_text.strip()



    