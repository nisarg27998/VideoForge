"""
Icon Generator for VideoForge
Creates application icon programmatically
"""

def create_icon(icon_path: str):
    """Create application icon"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a 64x64 icon for better quality
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw main video frame
        draw.rectangle([8, 16, 56, 48], fill='#00A8E8', outline='#ffffff', width=3)
        
        # Draw film strip holes
        holes = [(4, 12), (4, 20), (4, 28), (4, 36), (4, 44), (4, 52),
                 (60, 12), (60, 20), (60, 28), (60, 36), (60, 44), (60, 52)]
        
        for x, y in holes:
            draw.rectangle([x-2, y-2, x+2, y+2], fill='#ffffff')
        
        # Draw play button triangle
        draw.polygon([(24, 24), (24, 40), (40, 32)], fill='#ffffff')
        
        # Draw gear icon overlay for processing
        gear_center = (48, 16)
        gear_radius = 6
        draw.ellipse([gear_center[0]-gear_radius, gear_center[1]-gear_radius,
                     gear_center[0]+gear_radius, gear_center[1]+gear_radius], 
                     fill='#FFA500', outline='#ffffff', width=1)
        
        # Save as ICO
        img.save(icon_path, format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
        
    except ImportError:
        # Fallback: create a minimal placeholder
        create_minimal_icon(icon_path)


def create_minimal_icon(icon_path: str):
    """Create minimal icon without PIL"""
    # Create a very basic ICO file structure
    ico_header = bytes([
        0x00, 0x00,  # Reserved
        0x01, 0x00,  # ICO type
        0x01, 0x00,  # Number of images
        0x20, 0x20,  # Width, Height
        0x00,        # Colors in palette
        0x00,        # Reserved
        0x01, 0x00,  # Color planes
        0x20, 0x00,  # Bits per pixel
        0x00, 0x04, 0x00, 0x00,  # Size of image data
        0x16, 0x00, 0x00, 0x00   # Offset to image data
    ])
    
    # Minimal bitmap data (32x32, simplified)
    bitmap_data = b'\x00' * 1024  # Placeholder bitmap
    
    try:
        with open(icon_path, 'wb') as f:
            f.write(ico_header + bitmap_data)
    except Exception as e:
        print(f"Could not create icon: {e}")