import streamlit as st
from PIL import Image, ImageFilter
import io
import numpy as np

# Try to import rembg, but make it optional
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    st.warning("Background removal feature is not available. Install 'rembg' to enable it.")

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
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🖼️ Image Manipulation Studio")
st.markdown("Upload an image and use our tools to manipulate, resize, or convert formats.")

# Sidebar for navigation
st.sidebar.title("Navigation")
tools = ["📐 Image Resizing", "🔄 Format Conversion"]
if REMBG_AVAILABLE:
    tools.insert(0, "🎨 Background Removal")
else:
    tools.append("🎨 Simple Background Effects")

tool_choice = st.sidebar.radio("Select a tool:", tools)

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

# Function for simple background effects (alternative to rembg)
def apply_simple_background_effect(image, effect_type="blur"):
    """Apply simple background effects without ML-based removal"""
    if effect_type == "blur":
        # Apply Gaussian blur
        blurred = image.filter(ImageFilter.GaussianBlur(radius=10))
        return blurred
    elif effect_type == "grayscale":
        # Convert to grayscale
        return image.convert("L").convert("RGBA")
    elif effect_type == "white":
        # Create white background
        white_bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
        if image.mode == "RGBA":
            white_bg.paste(image, (0, 0), image)
            return white_bg
        return image
    return image

# Background Removal Tool
if tool_choice == "🎨 Background Removal" and REMBG_AVAILABLE:
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

# Simple Background Effects (Alternative when rembg is not available)
elif tool_choice == "🎨 Simple Background Effects":
    st.header("Simple Background Effects")
    st.info("Apply simple background effects to your images. For advanced background removal, install the 'rembg' package.")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'webp', 'bmp'],
        key="bg_effects"
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
        
        # Effect selection
        effect_type = st.selectbox(
            "Choose an effect:",
            ["Blur Background", "Grayscale", "White Background"]
        )
        
        effect_map = {
            "Blur Background": "blur",
            "Grayscale": "grayscale",
            "White Background": "white"
        }
        
        # Process button
        if st.button("Apply Effect", type="primary"):
            with st.spinner("Applying effect..."):
                try:
                    # Apply effect
                    output_image = apply_simple_background_effect(
                        image, 
                        effect_map[effect_type]
                    )
                    
                    # Display result
                    with col2:
                        st.subheader("Effect Applied")
                        st.image(output_image, use_column_width=True)
                        display_image_info(output_image)
                    
                    # Download button
                    img_bytes = pil_to_bytes(output_image)
                    st.success("Effect applied successfully!")
                    st.download_button(
                        label="Download Image",
                        data=img_bytes.getvalue(),
                        file_name=f"effect_{effect_map[effect_type]}.png",
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
            
            maintain_ratio = st.checkbox("Maintain aspect ratio", value=True)
            
            with col1:
                new_width = st.number_input(
                    "Width (px)",
                    min_value=1,
                    max_value=10000,
                    value=image.width,
                    key="width_input"
                )
            with col2:
                if maintain_ratio:
                    aspect_ratio = image.width / image.height
                    new_height = int(new_width / aspect_ratio)
                    st.metric("Height (px)", new_height)
                else:
                    new_height = st.number_input(
                        "Height (px)",
                        min_value=1,
                        max_value=10000,
                        value=image.height,
                        key="height_input"
                    )
        
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
        
        # Calculate size reduction
        original_pixels = image.width * image.height
        new_pixels = new_width * new_height
        size_change = ((new_pixels - original_pixels) / original_pixels) * 100
        
        if size_change < 0:
            st.caption(f"📉 Image will be reduced by {abs(size_change):.1f}%")
        elif size_change > 0:
            st.caption(f"📈 Image will be enlarged by {size_change:.1f}%")
        
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
        
        current_format = image.format if image.format else "Unknown"
        st.caption(f"Current format: {current_format}")
        
        target_format = st.selectbox(
            "Select target format:",
            list(formats.keys())
        )
        
        # Show format-specific options
        quality = None
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
        
        # Handle transparency
        bg_color = "#FFFFFF"
        if image.mode == "RGBA" and not formats[target_format]["supports_transparency"]:
            st.warning(f"⚠️ {target_format} doesn't support transparency. The transparent areas will be filled with the background color.")
            bg_color = st.color_picker("Choose background color for transparent areas:", "#FFFFFF")
        
        # Show format comparison
        with st.expander("Format Comparison"):
            st.markdown(f"""
            **{target_format} Format Characteristics:**
            - Transparency support: {'✅ Yes' if formats[target_format]["supports_transparency"] else '❌ No'}
            - Compression: {'Lossy' if target_format in ['JPEG', 'WebP'] else 'Lossless'}
            - Best for: {'Photos' if target_format == 'JPEG' else 'Graphics with transparency' if target_format == 'PNG' else 'Web images' if target_format == 'WebP' else 'General use'}
            """)
        
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
                    if converted_image.mode not in ["RGB", "L"]:
                        converted_image = converted_image.convert("RGB")
                elif target_format == "BMP":
                    # BMP doesn't support RGBA, convert to RGB
                    if converted_image.mode == "RGBA":
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
        <p>Made with ❤️ By Adnan Akram | Image Manipulation Studio</p>
        <p style='font-size: 0.8em;'>For advanced background removal, install 'rembg' package</p>
    </div>
    """,
    unsafe_allow_html=True
)
