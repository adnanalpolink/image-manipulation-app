import streamlit as st
from PIL import Image
import io
from rembg import remove
import numpy as np

# Configure the Streamlit page
st.set_page_config(
    page_title="Image Manipulation Studio",
    page_icon="🖼️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🖼️ Image Manipulation Studio")
st.markdown("Upload an image and use our tools to remove backgrounds, resize, or convert formats.")

# Sidebar for navigation
st.sidebar.title("Navigation")
tool_choice = st.sidebar.radio(
    "Select a tool:",
    ["🎨 Background Removal", "📐 Image Resizing", "🔄 Format Conversion"]
)

# Function to convert PIL Image to bytes
def pil_to_bytes(img, format="PNG"):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=format)
    img_byte_arr.seek(0)
    return img_byte_arr

# Function to display image info
def display_image_info(image):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Width", f"{image.width} px")
    with col2:
        st.metric("Height", f"{image.height} px")
    with col3:
        st.metric("Format", image.format if image.format else "Unknown")

# Background Removal Tool
if tool_choice == "🎨 Background Removal":
    st.header("Background Removal Tool")
    st.info("Upload an image to automatically remove its background. Works best with images that have clear subjects.")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'webp', 'bmp'],
        key="bg_removal"
    )
    
    if uploaded_file is not None:
        # Create two columns for before/after
        col1, col2 = st.columns(2)
        
        # Load and display original image
        with col1:
            st.subheader("Original Image")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
            display_image_info(image)
        
        # Process button
        if st.button("Remove Background", type="primary"):
            with st.spinner("Removing background... This may take a moment."):
                try:
                    # Convert image to bytes for rembg
                    img_bytes = pil_to_bytes(image)
                    
                    # Remove background
                    output_bytes = remove(img_bytes.getvalue())
                    
                    # Convert back to PIL Image
                    output_image = Image.open(io.BytesIO(output_bytes))
                    
                    # Display result
                    with col2:
                        st.subheader("Background Removed")
                        st.image(output_image, use_column_width=True)
                        display_image_info(output_image)
                    
                    # Download button
                    st.success("Background removed successfully!")
                    st.download_button(
                        label="Download Image (PNG)",
                        data=output_bytes,
                        file_name="background_removed.png",
                        mime="image/png"
                    )
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Image Resizing Tool
elif tool_choice == "📐 Image Resizing":
    st.header("Image Resizing Tool")
    st.info("Resize your images by percentage or to specific dimensions while maintaining aspect ratio.")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'webp', 'bmp'],
        key="resize"
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        # Display original image
        st.subheader("Original Image")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.image(image, use_column_width=True)
        with col2:
            display_image_info(image)
        
        st.divider()
        
        # Resize options
        resize_method = st.radio(
            "Choose resize method:",
            ["Percentage", "Custom Dimensions", "Preset Sizes"]
        )
        
        new_width, new_height = image.width, image.height
        
        if resize_method == "Percentage":
            percentage = st.slider(
                "Resize percentage:",
                min_value=10,
                max_value=200,
                value=100,
                step=5,
                help="100% = original size"
            )
            new_width = int(image.width * percentage / 100)
            new_height = int(image.height * percentage / 100)
            
        elif resize_method == "Custom Dimensions":
            col1, col2 = st.columns(2)
            with col1:
                new_width = st.number_input(
                    "Width (px)",
                    min_value=1,
                    max_value=10000,
                    value=image.width
                )
            with col2:
                new_height = st.number_input(
                    "Height (px)",
                    min_value=1,
                    max_value=10000,
                    value=image.height
                )
            
            maintain_ratio = st.checkbox("Maintain aspect ratio", value=True)
            if maintain_ratio:
                aspect_ratio = image.width / image.height
                if st.session_state.get('last_changed') == 'width':
                    new_height = int(new_width / aspect_ratio)
                else:
                    new_width = int(new_height * aspect_ratio)
        
        else:  # Preset Sizes
            preset = st.selectbox(
                "Select preset size:",
                [
                    "Thumbnail (150x150)",
                    "Small (320x240)",
                    "Medium (640x480)",
                    "Large (1024x768)",
                    "HD (1920x1080)",
                    "Instagram Square (1080x1080)",
                    "Instagram Portrait (1080x1350)",
                    "Twitter (1200x675)",
                    "Facebook Cover (820x312)"
                ]
            )
            
            preset_sizes = {
                "Thumbnail (150x150)": (150, 150),
                "Small (320x240)": (320, 240),
                "Medium (640x480)": (640, 480),
                "Large (1024x768)": (1024, 768),
                "HD (1920x1080)": (1920, 1080),
                "Instagram Square (1080x1080)": (1080, 1080),
                "Instagram Portrait (1080x1350)": (1080, 1350),
                "Twitter (1200x675)": (1200, 675),
                "Facebook Cover (820x312)": (820, 312)
            }
            
            new_width, new_height = preset_sizes[preset]
        
        # Show preview dimensions
        st.info(f"New dimensions: {new_width} x {new_height} px")
        
        # Resize button
        if st.button("Resize Image", type="primary"):
            try:
                # Perform resize
                resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Display result
                st.subheader("Resized Image")
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(resized_image, use_column_width=True)
                with col2:
                    display_image_info(resized_image)
                
                # Download button
                img_format = image.format if image.format else "PNG"
                img_bytes = pil_to_bytes(resized_image, format=img_format)
                
                st.success("Image resized successfully!")
                st.download_button(
                    label=f"Download Resized Image ({img_format})",
                    data=img_bytes.getvalue(),
                    file_name=f"resized_{new_width}x{new_height}.{img_format.lower()}",
                    mime=f"image/{img_format.lower()}"
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Format Conversion Tool
else:  # Format Conversion
    st.header("Image Format Conversion Tool")
    st.info("Convert your images between different formats including JPG, PNG, WebP, BMP, and more.")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif', 'tiff'],
        key="convert"
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        # Display original image
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Original Image")
            st.image(image, use_column_width=True)
        with col2:
            display_image_info(image)
        
        st.divider()
        
        # Format selection
        st.subheader("Conversion Settings")
        
        formats = {
            "PNG": {"extension": "png", "mime": "image/png", "supports_transparency": True},
            "JPEG": {"extension": "jpg", "mime": "image/jpeg", "supports_transparency": False},
            "WebP": {"extension": "webp", "mime": "image/webp", "supports_transparency": True},
            "BMP": {"extension": "bmp", "mime": "image/bmp", "supports_transparency": False},
            "GIF": {"extension": "gif", "mime": "image/gif", "supports_transparency": True},
            "TIFF": {"extension": "tiff", "mime": "image/tiff", "supports_transparency": True}
        }
        
        target_format = st.selectbox(
            "Select target format:",
            list(formats.keys())
        )
        
        # Show format-specific options
        if target_format == "JPEG":
            quality = st.slider(
                "JPEG Quality:",
                min_value=1,
                max_value=100,
                value=85,
                help="Higher values mean better quality but larger file size"
            )
        elif target_format == "WebP":
            quality = st.slider(
                "WebP Quality:",
                min_value=1,
                max_value=100,
                value=80,
                help="Higher values mean better quality but larger file size"
            )
        else:
            quality = None
        
        # Handle transparency
        if image.mode == "RGBA" and not formats[target_format]["supports_transparency"]:
            st.warning(f"⚠️ {target_format} doesn't support transparency. The transparent areas will be filled with the background color.")
            bg_color = st.color_picker("Choose background color for transparent areas:", "#FFFFFF")
        
        # Convert button
        if st.button("Convert Image", type="primary"):
            try:
                # Handle transparency if needed
                if image.mode == "RGBA" and not formats[target_format]["supports_transparency"]:
                    # Create a new image with background color
                    background = Image.new("RGB", image.size, bg_color)
                    background.paste(image, mask=image.split()[-1])
                    converted_image = background
                else:
                    converted_image = image
                
                # Prepare save parameters
                save_params = {}
                if quality is not None:
                    save_params['quality'] = quality
                if target_format == "PNG":
                    save_params['optimize'] = True
                
                # Convert and save
                output = io.BytesIO()
                if target_format == "JPEG":
                    # Ensure RGB mode for JPEG
                    if converted_image.mode != "RGB":
                        converted_image = converted_image.convert("RGB")
                converted_image.save(output, format=target_format, **save_params)
                output.seek(0)
                
                # Success message and download
                st.success(f"Image converted to {target_format} successfully!")
                
                # Show file size comparison
                original_size = len(uploaded_file.getvalue())
                converted_size = len(output.getvalue())
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Original Size", f"{original_size / 1024:.1f} KB")
                with col2:
                    st.metric("Converted Size", f"{converted_size / 1024:.1f} KB")
                with col3:
                    size_diff = ((converted_size - original_size) / original_size) * 100
                    st.metric("Size Change", f"{size_diff:+.1f}%")
                
                # Download button
                st.download_button(
                    label=f"Download {target_format} Image",
                    data=output.getvalue(),
                    file_name=f"converted.{formats[target_format]['extension']}",
                    mime=formats[target_format]['mime']
                )
                
            except Exception as e:
                st.error(f"An error occurred during conversion: {str(e)}")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Made with ❤️ By Adnan Akram | Image Manipulation Studio
    </div>
    """,
    unsafe_allow_html=True
)
