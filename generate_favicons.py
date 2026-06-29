import os
from PIL import Image

def generate_favicons():
    source = 'icon.png'
    dest_dir = 'frontend/public'
    
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        
    try:
        img = Image.open(source)
    except Exception as e:
        print(f"Error opening {source}: {e}")
        return

    # Generate regular pngs
    sizes = {
        'favicon-16x16.png': (16, 16),
        'favicon-32x32.png': (32, 32),
        'favicon-48x48.png': (48, 48),
        'apple-touch-icon.png': (180, 180),
        'android-chrome-192x192.png': (192, 192),
        'android-chrome-512x512.png': (512, 512),
    }

    for filename, size in sizes.items():
        resized = img.resize(size, Image.Resampling.LANCZOS)
        resized.save(os.path.join(dest_dir, filename))
        print(f"Generated {filename}")

    # Generate .ico (which can contain multiple sizes, typically 16, 32, 48)
    ico_sizes = [(16, 16), (32, 32), (48, 48)]
    img.save(os.path.join(dest_dir, 'favicon.ico'), format='ICO', sizes=ico_sizes)
    print("Generated favicon.ico")

if __name__ == '__main__':
    generate_favicons()
