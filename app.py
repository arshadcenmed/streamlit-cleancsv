import streamlit as st
import pandas as pd
import csv
import chardet
from io import StringIO, BytesIO
import base64

# Streamlit app title
st.title('ASCII characters checker')
st.text('This app will first check the csv file format.')
st.text('It will then check the CSV file for any ASCII characters and convert them into searchable strings.')
st.text('If found, download the file and search for <0x in your text editor.')

# File uploader allows user to add their own CSV
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

# Checkbox for user to choose encoding conversion
convert_to_utf8 = st.checkbox("Convert file to UTF-8", value=True)

if uploaded_file is not None:
    # To read file as string:
    bytes_data = uploaded_file.getvalue()
    
    # Detect the encoding of the uploaded file
    result = chardet.detect(bytes_data[:1024])  # Reading a sample for efficiency
    original_encoding = result['encoding']
    st.write(f"Detected encoding: {original_encoding}")  # Display the detected encoding
    
    # If the user wants to convert to UTF-8 and the file is not already UTF-8, convert it
    if convert_to_utf8 and original_encoding != 'utf-8':
        string_data = bytes_data.decode(original_encoding)  # Decode using the detected encoding
        bytes_data = string_data.encode('utf-8')  # Encode to UTF-8
    elif not convert_to_utf8:
        # If user does not want to convert to UTF-8, ensure it's in ASCII
        string_data = bytes_data.decode(original_encoding, errors='replace')  # Decode with replacement
        bytes_data = string_data.encode('ascii', errors='replace')  # Encode to ASCII with replacement for non-ASCII characters
    
    # Convert bytes data to a StringIO object for pandas
    string_io_data = StringIO(bytes_data.decode('utf-8' if convert_to_utf8 else 'ascii'))
    
    # Define a mapping of non-printable ASCII characters to their visible equivalents
    ascii_replacements = {
        i: f'<0x{i:02X}>' for i in range(128) if not chr(i).isprintable()
    }
    
    # Function to replace non-printable ASCII characters
    def replace_ascii_chars(s):
        if isinstance(s, str):
            return ''.join(ascii_replacements.get(ord(char), char) for char in s)
        elif pd.isnull(s):
            return s  # Return as is if the value is NaN
        else:
            return str(s)  # Convert non-string, non-null values to string
    
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(string_io_data, sep=',')
    
    # Apply the function to every cell in the DataFrame
    cleaned_df = df.applymap(replace_ascii_chars)
    
    # Check if ASCII characters were found and replaced
    ascii_found = any('<0x' in str(cell) for row in cleaned_df.values for cell in row)
    if ascii_found:
        # Display a message indicating that ASCII characters were found and replaced
        st.info('ASCII characters were found and have been replaced with searchable strings.')
    else:
        # Optionally, display a message if no ASCII characters were found
        st.write('No ASCII characters were found in the file.')
    
    # Convert DataFrame to CSV for download
    output_csv = cleaned_df.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC, encoding='utf-8' if convert_to_utf8 else 'ascii')
    
    # Create a link for downloading the cleaned CSV
    b64 = base64.b64encode(output_csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="cleaned_file.csv">Download cleaned CSV file</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    st.write('File cleaned and ready for download.')