import streamlit as st
import pandas as pd
import csv
import chardet
from io import StringIO, BytesIO

# Streamlit app title
st.title('CSV File Cleaner')

# File uploader allows user to add their own CSV
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

if uploaded_file is not None:
    # To read file as string:
    bytes_data = uploaded_file.getvalue()
    
    # Detect the encoding of the uploaded file
    result = chardet.detect(bytes_data[:1024])  # Reading a sample for efficiency
    original_encoding = result['encoding']
    st.write(f"Detected encoding: {original_encoding}")  # Display the detected encoding
    
    # If the file is not already UTF-8, convert it
    if original_encoding != 'utf-8':
        string_data = bytes_data.decode(original_encoding)  # Decode using the detected encoding
        bytes_data = string_data.encode('utf-8')  # Encode to UTF-8
    
    # Convert bytes data to a StringIO object for pandas
    string_io_data = StringIO(bytes_data.decode('utf-8'))
    
    # Define a mapping of non-printable ASCII characters to their visible equivalents
    ascii_replacements = {
        i: f'<0x{i:02X}>' for i in range(128) if not chr(i).isprintable()
    }
    
    # Function to replace non-printable ASCII characters
    def replace_ascii_chars(s):
        if isinstance(s, str):
            return ''.join(ascii_replacements.get(ord(char), char) for char in s)
        return s
    
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(string_io_data, sep=',')
    
    # Apply the function to every cell in the DataFrame
    cleaned_df = df.applymap(replace_ascii_chars)
    
    # Convert DataFrame to CSV for download
    output_csv = cleaned_df.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC, encoding='utf-8')
    
    # Create a link for downloading the cleaned CSV
    b64 = base64.b64encode(output_csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="cleaned_file.csv">Download cleaned CSV file</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    st.write('File cleaned and ready for download.')