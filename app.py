import streamlit as st
from PIL import Image
import json
import io

st.set_page_config(
    page_title="Repix - NFT Image Generator",
    page_icon="🎨",
    layout="centered"
)

def validate_json_format(json_data):
    """Validate the JSON format"""
    if not isinstance(json_data, dict) or 'pixels' not in json_data:
        raise ValueError("JSON must contain a 'pixels' object")
    
    if not json_data['pixels']:
        raise ValueError("No pixel data found")
    
    for coord, color in json_data['pixels'].items():
        if not isinstance(color, list) or len(color) != 3:
            raise ValueError(f"Invalid color format for coordinate {coord}")
        if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
            raise ValueError(f"Color values must be integers between 0 and 255 for coordinate {coord}")

def process_pixel_data(json_data):
    # Find the actual dimensions by looking at the pixel coordinates
    max_x = max(int(coord.split(',')[0]) for coord in json_data['pixels'].keys())
    max_y = max(int(coord.split(',')[1]) for coord in json_data['pixels'].keys())
    width = max_x + 1
    height = max_y + 1
    
    # Calculate scale factor to fit the larger dimension to 2000 pixels
    scale_factor = min(2000 // width, 2000 // height)
    final_width = width * scale_factor
    final_height = height * scale_factor
    
    # Create a new image
    img = Image.new('RGB', (final_width, final_height), color='black')
    pixels = img.load()
    
    # Set each pixel's color, scaling up
    for coord, color in json_data['pixels'].items():
        x, y = map(int, coord.split(','))
        # Fill a square for each pixel
        for dx in range(scale_factor):
            for dy in range(scale_factor):
                pixels[x * scale_factor + dx, y * scale_factor + dy] = tuple(color)
    
    return img

def main():
    st.title("🎨 Repix - NFT Image Generator")
    st.write("Transform your pixel data into high-resolution NFT images")
    
    uploaded_file = st.file_uploader("Upload your pixel data JSON file", type="json")
    
    if uploaded_file is not None:
        try:
            # Load JSON data
            json_data = json.load(uploaded_file)
            validate_json_format(json_data)
            
            # Process the image
            with st.spinner("✨ Generating your NFT image..."):
                img = process_pixel_data(json_data)
                
                # Convert PIL image to bytes for downloading
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                # Create columns for layout
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Display the image
                    st.image(img, caption="Generated NFT Image", use_column_width=True)
                
                with col2:
                    # Add download button
                    st.download_button(
                        label="⬇️ Download NFT Image",
                        data=img_bytes.getvalue(),
                        file_name="repix_nft.png",
                        mime="image/png",
                        help="Click to download your generated NFT image"
                    )
                    
                    # Display image info
                    st.info(f"Image Size: {img.size[0]}x{img.size[1]} pixels")
                    
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please check the file format.")
        except ValueError as e:
            st.error(f"Invalid data format: {str(e)}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 