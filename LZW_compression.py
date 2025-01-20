import streamlit as st
import time
import io

# LZW Encoding Function
def encoding(s1, initial_dict_size=256, max_table_size=4096, reset_threshold=None):
    start_time = time.perf_counter()  # Use perf_counter for high-resolution timing
    table = {chr(i): i for i in range(initial_dict_size)}
    p = ""
    code = initial_dict_size
    output_code = []

    for c in s1:
        new_string = p + c
        if new_string in table:
            p = new_string
        else:
            output_code.append(table[p])
            if len(table) < max_table_size:
                table[new_string] = code
                code += 1

            if reset_threshold and code >= reset_threshold:
                table = {chr(i): i for i in range(initial_dict_size)}
                code = initial_dict_size

            p = c

    if p:
        output_code.append(table[p])

    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
    return output_code, elapsed_time

# LZW Decoding Function
def decoding(op, initial_dict_size=256):
    start_time = time.perf_counter()  # Use perf_counter for high-resolution timing
    table = {i: chr(i) for i in range(initial_dict_size)}
    old = op[0]
    s = table[old]
    result = s

    count = initial_dict_size

    for n in op[1:]:
        if n not in table:
            s = table[old] + s[0]
        else:
            s = table[n]

        result += s
        table[count] = table[old] + s[0]
        count += 1
        old = n

    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
    return result, elapsed_time

# Function to convert data to downloadable format
def convert_to_downloadable_file(data, filename):
    # Convert list of integers (compressed output) to bytes for download
    if isinstance(data, list):  # if data is a list (like compressed data)
        data = " ".join(map(str, data)).encode('utf-8')
    else:
        data = data.encode('utf-8')  # for text data or decompressed text
    
    # Create a BytesIO object
    byte_io = io.BytesIO(data)
    byte_io.seek(0)
    
    return byte_io

# Streamlit UI
def main():
    st.image("https://devopedia.org/images/article/159/4139.1553071738.jpg", use_container_width=True)
    st.title("LZW Compression and Decompression for Text Files")
    st.subheader("Compress and decompress text files using LZW algorithm")

    st.write("Upload a text file to compress, download the compressed data, then decompress it back to the original text file.")

    # File uploader to upload a text file
    uploaded_file = st.file_uploader("Choose a text file", type="txt")

    if uploaded_file is not None:
        # Read the uploaded file's content
        text_data = uploaded_file.read().decode("utf-8")  # Decoding from bytes to string
        
        # Display the uploaded text (first 1000 characters)
        st.text_area("Uploaded Text", text_data[:1000] + "...", height=300)
        
        # Original text size (in characters)
        original_size = len(text_data)
        st.write(f"Original text size: {original_size} characters")
    else:
        # Display a message if no file is uploaded
        st.write("Please upload a text file to continue.")  # Show the first 1000 characters to avoid overloading

    # Store the file in session state for decompression later
    if 'compressed_text_output' not in st.session_state:
        st.session_state['compressed_text_output'] = None

    # Parameter Inputs using sliders
    with st.sidebar:
        st.header("Compression Parameters")
        initial_dict_size = st.slider("Initial Dictionary Size:", min_value=1, max_value=512, value=256, step=1)
        max_table_size = st.slider("Maximum Table Size:", min_value=256, max_value=8192, value=4096, step=256)
        reset_threshold = st.slider("Reset Threshold (optional):", min_value=0, max_value=max_table_size, value=0, step=256)

    if st.button("Compress the Text File"):
        # Compress the text data
        compressed_output, compression_time = encoding(text_data, initial_dict_size, max_table_size, reset_threshold)
        compressed_size = len(str(compressed_output))  # Size of compressed output (as a string)

        # Calculate compression ratio (original size vs compressed size)
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0

        st.success(f"Text compression completed in {compression_time:.2f} ms")
        st.write(f"Original Size: {original_size} characters")
        st.write(f"Compressed Size: {compressed_size} characters")
        st.write(f"Compression Ratio: {compression_ratio:.2f}")

        # Save compressed output in session state for later use
        st.session_state['compressed_text_output'] = compressed_output

        # Create downloadable compressed text data (LZW compressed)
        compressed_file_txt = convert_to_downloadable_file(compressed_output, "compressed_text_output.txt")
        st.download_button("Download Compressed Text Data (TXT)", compressed_file_txt, file_name="compressed_text_output.txt")

    if st.button("Decompress the Text File") and st.session_state['compressed_text_output'] is not None:
        # Decompress the text data
        decompressed_text, decompression_time = decoding(st.session_state['compressed_text_output'], initial_dict_size)
        st.success(f"Text decompression completed in {decompression_time:.2f} ms")

        # Provide downloadable decompressed text
        decompressed_file_txt = convert_to_downloadable_file(decompressed_text, "decompressed_text.txt")
        st.download_button("Download Decompressed Text", decompressed_file_txt, file_name="decompressed_text.txt")

        # Check if decompressed text is the same as the original
        if text_data == decompressed_text:
            st.success("The decompressed text is the same as the original. Lossless decompression successful!")
        else:
            st.error("The decompressed text does not match the original. There is a loss during decompression.")

    # Run compression for different parameter combinations and provide download links for each output
    st.subheader("Compression with Different Parameters")

    # Try different parameter values
    param_combinations = [
        {"initial_dict_size": 128, "max_table_size": 2048, "reset_threshold": 0},
        {"initial_dict_size": 256, "max_table_size": 4096, "reset_threshold": 256},
        {"initial_dict_size": 512, "max_table_size": 8192, "reset_threshold": 1024},
    ]

    for params in param_combinations:
        if st.button(f"Compress with {params}"):
            compressed_output, compression_time = encoding(text_data, **params)
            compressed_size = len(str(compressed_output))
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
            st.write(f"Compression Parameters: {params}")
            st.write(f"Compression completed in {compression_time:.2f} ms")
            st.write(f"Compression Ratio: {compression_ratio:.2f}")

            # Create downloadable file for each parameter combination
            compressed_file_txt = convert_to_downloadable_file(compressed_output, f"compressed_{params['initial_dict_size']}_{params['max_table_size']}.txt")
            st.download_button(f"Download Compressed File ({params['initial_dict_size']}_{params['max_table_size']})", 
                               compressed_file_txt, 
                               file_name=f"compressed_{params['initial_dict_size']}_{params['max_table_size']}.txt")

if __name__ == "__main__":
    main()
