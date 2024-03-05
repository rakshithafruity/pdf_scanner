from flask import Flask, render_template, request, session
import io
import urllib3
import PyPDF2
import py_pdf_parser
import fitz
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
from io import BytesIO
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser, PDFSyntaxError
import re
import joblib


def get_pdf_size(info):
    try:

        size_bytes = len(info.encode('utf-8'))
        size_kb = size_bytes / 1024

        return size_kb
    except FileNotFoundError:
        return -1

def get_pdf_metadata_size(info):
    try:

        metadata_size = len(info.encode('utf-8'))
        return metadata_size
    except:
        print(f"Error reading PDF:")
        return -1



def get_pdf_page_count(info):
    try:
        page_count = int(info.count('\f'))+1
        return page_count
    except Exception as e:
        print(e)
        return -1
    
def check_pdf_xref(info):

    try:
        # Find the number of Xref entries in the PDF content
        xref_count = info.count('/XRef')

        # Return the formatted Xref table information as a string
        return xref_count
    except Exception as e:
        print(f"Error checking PDF XRef: {e}")
        return -1
def get_pdf_title(info):
    try:

        # Ensure info is in bytes-like object
        if isinstance(info, str):
            info = info.encode('utf-8')  # Convert str to bytes

        # Parse the PDF content
        parser = PDFParser(BytesIO(info))
        document = PDFDocument(parser)

        # Extract title from metadata list
        title = "0"  # Default value if no title is found
        for item in document.info:
            if isinstance(item, tuple) and len(item) == 2 and item[0] == b"/Title":
                title = item[1].decode('utf-8')  # Decode the bytes to str
                break

        # Return the title characters
        return title
    except Exception as e:
        print(f"Error reading PDF title: {e}")
        return e
def check_pdf_encryption(info):
    info=info.encode('utf-8')
    try:
        # Attempt to extract text from the PDF content
        text = extract_text(info)
        # PDF not encrypted
        return 0
    except PDFSyntaxError as e:
        if 'encrypted' in str(e):
            return 1
        else:
            # PDF syntax error occurred
            print("Error processing PDF: " + str(e))
            return -1
    except Exception as ex:
        # Other exceptions occurred
        print("Error processing PDF: " + str(ex))
        return -1


def list_embedded_files(info):
    embedded_files_dict = {}  # Create a new dictionary to store embedded files information
    try:
        info=info.encode('utf-8')
        # Open the PDF content
        pdf_document = fitz.open(stream=info, filetype="pdf")

        # Flag to check if any embedded files are found
        found_files = False

        # Iterate through each page
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]

            # Get the page's XObject dictionary (graphics objects)
            xobjects = page.get_images(full=True)

            # Iterate through the XObjects to find embedded files
            for xobject_index, xobject_info in enumerate(xobjects):
                # Check if the XObject has an embedded file
                xobject_index += 1  # Adding 1 to start the index from 1
                if "imagemask" in xobject_info and "image" in xobject_info:
                    # Add information about the embedded file to the dictionary
                    embedded_files_dict[f'Embedded File {xobject_index}'] = xobject_info['title']
                    found_files = True

        # Close the PDF file
        pdf_document.close()

        # Set the count of embedded files in the dictionary
        if not found_files:
            embedded_files_dict['embedded files'] = 0
    except Exception as e:
        print(f"Error listing embedded files: {e}")

    return embedded_files_dict  # Return the dictionary containing embedded files information
def count_images_in_pdf(info):
    info=info.encode('utf-8')

    images_dict = {}  # Create a dictionary to store the result

    try:
        # Open the PDF content
        pdf_document = fitz.open(stream=info, filetype="pdf")

        # Variable to store the total number of images in the PDF
        total_images = 0

        # Iterate through each page
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]

            # Get the page's XObject dictionary (graphics objects)
            xobjects = page.get_images(full=True)

            # Increment the total_images count for each image found on the page
            total_images += len(xobjects)

        # Close the PDF file
        pdf_document.close()

        # Set the count of images in the dictionary
        images_dict['images'] = total_images

    except Exception as e:
        print(f"Error counting images in PDF: {e}")

    return images_dict  # Return the dictionary containing the total number of images
def is_text_present(info):
    info=info.encode('utf-8')
    try:
        # Initialize dictionary to store the result
        result_dict = {'text': ''}

        # Open the PDF content
        pdf_document = fitz.open(stream=info, filetype="pdf")

        # Iterate through pages
        for page_number in range(pdf_document.page_count):
            # Get the page
            page = pdf_document[page_number]

            # Extract text from the page
            text = page.get_text()

            # Check if text is present
            if text.strip():
                result_dict['text'] = '1'  # Set 'text' to '1' if text is present
                return result_dict

        # No text found in the PDF
        result_dict['text'] = '0'
        return result_dict

    except Exception as e:
        # An error occurred
        print(f"An error occurred1: {e}")
        result_dict['text'] = '-2'  # Set 'text' to '-2' for unclear
        return result_dict
import re

def count_objects(info):
    info=info.encode('utf-8')

    try:
        # Initialize dictionary
        result_dict = {'obj_count': ''}

        # Find occurrences of "obj"
        obj_positions = [match.start() for match in re.finditer(rb'\bobj\b', info)]

        # Count the total number of objects
        obj_count = len(obj_positions)

        # Set the number of "obj" occurrences
        result_dict['obj_count'] = obj_count

        return result_dict

    except Exception as e:
        # An error occurred
        print(f"An error occurred2: {e}")
        return -1  # Set obj_count to -1 in case of an error

def count_endobjs(info):
    info=info.encode('utf-8')
    try:
        # Initialize dictionary
        result_dict = {'endobj_count': ''}

        # Count occurrences of "endobj"
        endobj_count = len(re.findall(rb'\bendobj\b', info))

        # Set the number of "endobj" occurrences
        result_dict['endobj_count'] = endobj_count

        return result_dict

    except Exception as e:
        # An error occurred
        print(f"An error occurred3: {e}")
        return -1  # Set endobj_count to -1 in case of an error
def count_streams(info):
    info=info.encode('utf-8')
    try:
        # Initialize dictionary
        result_dict = {'stream_count': '', 'endstream_count': ''}

        # Count occurrences of "stream" and "endstream"
        stream_count = info.count(b'stream')
        endstream_count = info.count(b'endstream')

        # Set the counts in the result dictionary
        result_dict['stream_count'] = stream_count
        result_dict['endstream_count'] = endstream_count

        return result_dict

    except Exception as e:
        # An error occurred
        print(f"An error occurred4: {e}")
        return {'stream_count': -1, 'endstream_count': -1}  # Set counts to -1 in case of an error
def count_trailers(info):
    
    try:
        info=info.encode('utf-8')
        info = io.BytesIO(info)
        # Initialize dictionary
        result_dict = {'trailer_count': ''}

        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(info)

        # Get the number of trailers (revisions)
        
        trailer_count = len(pdf_reader.trailer)

        # Set the trailer count in the result dictionary
        result_dict['trailer_count'] = trailer_count

        return result_dict

    except Exception as e:
        # An error occurred
        print(f"An error occurred5: {e}")
        return -1  # Set trailer count to -1 in case of an error
def count_startxref(info):
    print("hii")
    info=info.encode('utf-8')
    try:
        # Initialize dictionary
        result_dict = {'startxref_count': ''}

        # Open the PDF content as a BytesIO object
        pdf_content = BytesIO(info)

        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_content)
        # Count occurrences of "startxref"
        startxref_count = pdf_content.getvalue().count(b'startxref')
    
        # Set the startxref count in the result dictionary
        result_dict['startxref_count'] = startxref_count

        return result_dict

    except Exception as e:
        # An error occurred
        print(f"An error occurred6: {e}")
        return -1  # Set startxref count to -1 in case of an error

# def get_pdf_pageno_count(info):
#     try:
#         # Extract text from the PDF content
#         text = extract_text_from_content(info)
        
#         # Count the occurrences of the page delimiter
#         page_count = text.count('\f') + 1

#         return {'pageno': page_count}  # Return page count as a dictionary

#     except PDFSyntaxError as e:
#         print(f"PDFSyntaxError: {e}")
#         return {'pageno': -1}  # Set page count to -1 in case of a syntax error

#     except Exception as ex:
#         print(f"Error processing PDF: {ex}")
#         return {'pageno': -1}  # Set page count to -1 in case of any other error
def count_js_keywords(info):
    info=info.encode('utf-8')
    try:
        # Open the PDF content
        pdf_document = fitz.open(stream=info, filetype="pdf")

        # Initialize counters for "/JS" and "/JavaScript" keywords
        js_count = 0
        javascript_count = 0

        # Iterate through pages
        for page_number in range(len(pdf_document)):
            # Get the page
            page = pdf_document.load_page(page_number)

            # Search for "/JS" and "/JavaScript" in the text
            text = page.get_text()
            js_count += text.lower().count('/js')
            javascript_count += text.lower().count('/javascript')

        # Return the counts as a dictionary
        return {'JS': js_count, 'javascript': javascript_count}

    except Exception as e:
        print(f"Error counting JS keywords: {e}")
        return {'JS': -1, 'javascript': -1}

def count_aa_openaction_keywords(info):
    info=info.encode('utf-8')
    try:
        # Open the PDF content
        pdf_document = fitz.open(stream=info, filetype="pdf")

        # Initialize counters for "/AA" and "/OpenAction" keywords
        aa_count = 0
        openaction_count = 0

        # Iterate through pages
        for page_number in range(len(pdf_document)):
            # Get the page
            page = pdf_document.load_page(page_number)

            # Search for "/AA" and "/OpenAction" in the text
            text = page.get_text()
            aa_count += text.lower().count('/aa')
            openaction_count += text.lower().count('/openaction')

        # Return the counts as a dictionary
        return {'AA': aa_count, 'OpenAction': openaction_count}

    except Exception as e:
        print(f"Error counting AA and OpenAction keywords: {e}")
        return {'AA': -1, 'OpenAction': -1}
def count_acroform_xfa_keywords(info):
    info=info.encode('utf-8')
    try:
        # Open the PDF content
        pdf_document = fitz.open(stream=info, filetype="pdf")

        # Initialize counters for "/AcroForm" and "/XFA" keywords
        acroform_count = 0
        xfa_count = 0

        # Iterate through pages
        for page_number in range(len(pdf_document)):
            # Get the page
            page = pdf_document.load_page(page_number)

            # Search for "/AcroForm" and "/XFA" in the text
            text = page.get_text()
            acroform_count += text.lower().count('/acroform')
            xfa_count += text.lower().count('/xfa')

        # Return the counts as a dictionary
        return {'Acroform': acroform_count, 'XFA': xfa_count}

    except Exception as e:
        print(f"Error counting AcroForm and XFA keywords: {e}")
        return {'Acroform': -1, 'XFA': -1}


def count_jbig2decode_colors_keywords(info):
    info=info.encode('utf-8')
    try:
        # Open the PDF content
        pdf_document = fitz.open(stream=info, filetype="pdf")

        # Initialize counters for "/JBIG2Decode" and "/Colors" keywords
        jbig2decode_count = 0
        colors_count = 0

        # Iterate through pages
        for page_number in range(len(pdf_document)):
            # Get the page
            page = pdf_document.load_page(page_number)

            # Search for "/JBIG2Decode" and "/Colors" in the text
            text = page.get_text()
            jbig2decode_count += text.lower().count('/jbig2decode')
            colors_count += text.lower().count('/colors')

        # Return the counts as a dictionary
        return {'JBIG2Decode': jbig2decode_count, 'Colors': colors_count}

    except Exception as e:
        print(f"Error counting JBIG2Decode and Colors keywords: {e}")
        return {'JBIG2Decode': -1, 'Colors': -1}
def count_richmedia_trailer_keywords(info):
    info=info.encode('utf-8')
    try:
        # Open the PDF content
        pdf_document = fitz.open(stream=info, filetype="pdf")

        # Initialize counters for "/RichMedia" and "/Trailer" keywords
        richmedia_count = 0
        trailer_count = 0

        # Iterate through pages
        for page_number in range(len(pdf_document)):
            # Get the page
            page = pdf_document.load_page(page_number)

            # Search for "/RichMedia" and "/Trailer" in the text
            text = page.get_text()
            richmedia_count += text.lower().count('/richmedia')
            trailer_count += text.lower().count('/trailer')

        # Return the counts as a dictionary
        return {'RichMedia': richmedia_count, 'Trailer': trailer_count}

    except Exception as e:
        print(f"Error counting RichMedia and Trailer keywords: {e}")
        return {'RichMedia': -1, 'Trailer': -1}


def count_uri_action_keywords(info):
    info=info.encode('utf-8')
    try:
        # Open the PDF content
        pdf_document = fitz.open(stream=info, filetype="pdf")

        # Initialize counters for "/URI" and "/Action" keywords
        uri_count = 0
        action_count = 0

        # Iterate through pages
        for page_number in range(len(pdf_document)):
            # Get the page
            page = pdf_document.load_page(page_number)

            # Search for "/URI" and "/Action" in the text
            text = page.get_text()
            uri_count += text.lower().count('/uri')
            action_count += text.lower().count('/action')

        # Return the counts as a dictionary
        return {'launch': uri_count, 'Action': action_count}

    except Exception as e:
        print(f"Error counting URI and Action keywords: {e}")
        return {'launch': -1, 'Action': -1}
def list_embedded_files(info):
    
    try:
        info=info.encode('utf-8')
        # Open the PDF content
        pdf_document = fitz.open(stream=info, filetype="pdf")

        # Flag to check if any embedded files are found
        found_files = False

        # Iterate through each page
        a={}
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)

            # Get the page's XObject dictionary (graphics objects)
            xobjects = page.get_images(full=True)

            # Iterate through the XObjects to find embedded files
            for xobject_index, xobject_info in enumerate(xobjects):
                # Check if the XObject has an embedded file
                xobject_index += 1  # Adding 1 to start the index from 1
                if "imagemask" in xobject_info and "image" in xobject_info:
                    # Print information about the embedded file
                    return [{'Embedded File': xobject_info['title']},{'embedded files': 0}]

        # Close the PDF content
        pdf_document.close()

        # Return a message if no embedded files are found
        return [{'embedded files': 0},{'Embedded File':0}]

    except Exception as e:
        print(f"Error listing embedded files: {e}")
        return [{'embedded files': -1},{'Embedded File':-1}]


def start(info):

    try:
        a1=list_embedded_files(info)

        a=[
            get_pdf_size(info), 
            get_pdf_metadata_size(info),
            get_pdf_page_count(info),
            check_pdf_xref(info),
            check_pdf_xref(info),
     get_pdf_title(info),
     a1[0]['embedded files'],
count_images_in_pdf(info)['images'],
is_text_present(info)['text'],
count_objects(info)['obj_count'],
    count_endobjs(info)['endobj_count'],
    count_streams(info)['stream_count'],
    count_streams(info)['endstream_count'],
    count_trailers(info)['trailer_count'],
    count_startxref(info)['startxref_count'],
            count_js_keywords(info)['JS'],
            count_js_keywords(info)['javascript'],
            count_aa_openaction_keywords(info)['AA'],
            count_aa_openaction_keywords(info)['OpenAction'],
            count_acroform_xfa_keywords(info)['Acroform'],
            count_acroform_xfa_keywords(info)['XFA'],
            count_jbig2decode_colors_keywords(info)['JBIG2Decode'],
            count_richmedia_trailer_keywords(info)['RichMedia'],
            count_uri_action_keywords(info)['launch'],
            a1[1]['Embedded File']]
        return a
    except Exception as e:
        print(e)
        return "0"


app = Flask(__name__)
app.secret_key = 'efleqfkhoqejf'
urllib3.disable_warnings()


@app.route('/', methods=['GET'])  # get ,post
def upload_file():
    session.clear()
    return render_template('index.html', e_flag=0)


@app.route('/getres', methods=['POST'])
def getres():
    file = request.files['file']
    if file:
        buff = io.BytesIO()
        buff.write(file.stream.read())
        buff.seek(0)

        try:
            info = buff.getvalue().decode('utf-8')
        except UnicodeDecodeError:
            try:
                info = buff.getvalue().decode('latin-1')  # Try a different encoding
            except Exception as e:
                print(f"Error decoding PDF content: {e}")
                return "Error decoding PDF content", 500

        try:
            result = start(info)
            trained_model = joblib.load('C:\\Users\\iamve\\OneDrive\\Desktop\\random_forest_model.joblib')
            predicted_output = trained_model.predict([result])
            if(predicted_output[0]==1):
                return "SAFE"
            else:
                 return "UNSAFE "
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return "Error processing PDF", 500


if __name__ == '__main__':
    app.run()