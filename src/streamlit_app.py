import streamlit as st
from PIL import Image
import json
import io

st.set_page_config(
    page_title="Repix - NFT Image Generator",
    page_icon="🎨",
    layout="wide"
)

def process_pixel_data(json_data):
    # Existing processing function remains the same
    max_x = max(int(coord.split(',')[0]) for coord in json_data['pixels'].keys())
    max_y = max(int(coord.split(',')[1]) for coord in json_data['pixels'].keys())
    width = max_x + 1
    height = max_y + 1
    
    scale_factor = min(2000 // width, 2000 // height)
    final_width = width * scale_factor
    final_height = height * scale_factor
    
    img = Image.new('RGB', (final_width, final_height), color='black')
    pixels = img.load()
    
    for coord, color in json_data['pixels'].items():
        x, y = map(int, coord.split(','))
        for dx in range(scale_factor):
            for dy in range(scale_factor):
                pixels[x * scale_factor + dx, y * scale_factor + dy] = tuple(color)
    
    return img

def main():
    st.title("🎨 Repix - NFT Image Generator")
    st.write("Transform your pixel data into high-resolution NFT images")
    
    # Allow multiple file uploads
    uploaded_files = st.file_uploader(
        "Upload your pixel data JSON files", 
        type="json",
        accept_multiple_files=True
    )
    
    if uploaded_files:
        # Create two columns: file list and preview
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Files")
            # Create a selectbox for file selection
            file_names = [f.name for f in uploaded_files]
            selected_file = st.selectbox(
                "Select a file to preview",
                file_names
            )
            
            # Add a download all button
            if st.button("⬇️ Download All Images"):
                for i, file in enumerate(uploaded_files):
                    try:
                        json_data = json.load(file)
                        img = process_pixel_data(json_data)
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        st.download_button(
                            label=f"Download {file.name}",
                            data=img_bytes.getvalue(),
                            file_name=f"repix_nft_{i+1}.png",
                            mime="image/png",
                            key=f"download_{i}"
                        )
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {str(e)}")
        
        with col2:
            st.subheader("Preview")
            # Find the selected file
            selected_index = file_names.index(selected_file)
            file = uploaded_files[selected_index]
            
            try:
                # Load and process the selected file
                json_data = json.load(file)
                with st.spinner("✨ Generating preview..."):
                    img = process_pixel_data(json_data)
                    
                    # Convert to bytes for downloading
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    
                    # Display image
                    st.image(img, caption=f"Preview: {file.name}", use_column_width=True)
                    
                    # Add download button for this image
                    col2_1, col2_2 = st.columns([1, 2])
                    with col2_1:
                        st.download_button(
                            label="⬇️ Download This Image",
                            data=img_bytes.getvalue(),
                            file_name=f"repix_nft_{selected_index+1}.png",
                            mime="image/png"
                        )
                    with col2_2:
                        st.info(f"Image Size: {img.size[0]}x{img.size[1]} pixels")
                        
            except json.JSONDecodeError:
                st.error(f"Invalid JSON file: {file.name}")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main() 