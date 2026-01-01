import os
import math
import numpy as np
from moviepy import ImageClip, concatenate_videoclips, CompositeVideoClip, ColorClip

# Parameters
OUTPUT_FILE = "output/test_infinity_effect.mp4"
IMAGES_DIR = "data/images"
DURATION_PER_IMAGE = 5  # seconds
SCREEN_SIZE = (1080, 1920) # Vertical generic size or 1920x1080 horizontal? 
# Usually manga recap are horizontal (YouTube). Let's stick to 1920x1080.
SCREEN_SIZE = (1920, 1080) 

def infinity_movement(t, duration):
    """
    Returns (x, y) displacement for a figure-8 motion (Lemniscate).
    t: current time
    duration: clip duration
    """
    # Normalized time 0 to 2*pi
    # Slow element: we want one loop or half loop per image?
    # Let's do one loop.
    u = (2 * math.pi * t) / duration
    
    # Amplitude of movement in pixels
    # We will scale the image to 110% so we have margin.
    # 1920 * 1.10 = 2112. Width diff = 192, so we can move +/- 96 px
    # 1080 * 1.10 = 1188. Height diff = 108, so we can move +/- 54 px
    
    A_x = 80
    A_y = 40
    
    # Parametric equations for Lemniscate of Bernoulli or Lissajous
    # Simple Lissajous for infinity shape: x = A sin(u), y = B sin(2u)
    
    x = A_x * math.sin(u)
    y = A_y * math.sin(2 * u)
    
    return (x, y)

def create_infinity_clip(image_path, duration):
    # 1. Load Image
    img = ImageClip(image_path)
    img_w, img_h = img.size
    screen_w, screen_h = SCREEN_SIZE
    
    # --- BACKGROUND (Blurred & Filling Screen) ---
    # We use "max" ratio to ensure the background covers the whole screen
    ratio_bg = max(screen_w / img_w, screen_h / img_h)
    bg_w = int(img_w * ratio_bg)
    bg_h = int(img_h * ratio_bg)
    
    # Resize and Center Background
    bg = img.resized((bg_w, bg_h))
    
    # Determine crop coordinates to center the background
    x_center = bg_w / 2
    y_center = bg_h / 2
    x1 = x_center - screen_w / 2
    y1 = y_center - screen_h / 2
    
    bg = bg.cropped(x1=x1, y1=y1, width=screen_w, height=screen_h)

    # Blur effect (simulated by darkening for speed/compatibility if blur is heavy, 
    # but let's try a simple opacity or layout trick). 
    # MoviePy Blur can be slow. A common trick is just darkening it significantly.
    bg = bg.with_opacity(0.3) # Darken background to make foreground pop
    
    # --- FOREGROUND (Main Image, Fit Height + Infinity Move) ---
    # We use "min" ratio to ensure the image fits in the screen
    ratio_fg = min(screen_w / img_w, screen_h / img_h)
    
    # Add 10% scale for movement margin so we don't see cutoffs when moving
    final_ratio_fg = ratio_fg * 1.10 
    
    new_w = int(img_w * final_ratio_fg)
    new_h = int(img_h * final_ratio_fg)
    
    fg = img.resized((new_w, new_h))
    
    # Center reference
    center_x = screen_w / 2
    center_y = screen_h / 2
    
    # Movement function
    def pos_func(t):
        dx, dy = infinity_movement(t, duration)
        # Center the image then apply displacement
        return (center_x - new_w/2 + dx, center_y - new_h/2 + dy)
    
    fg = fg.with_position(pos_func).with_duration(duration)
    bg = bg.with_duration(duration)
    
    # Composite: Black Base -> Blurred BG -> Animated FG
    base = ColorClip(size=SCREEN_SIZE, color=(0,0,0), duration=duration)
    return CompositeVideoClip([base, bg, fg], size=SCREEN_SIZE)

def main():
    # 1. Get 3 images
    all_files = sorted([f for f in os.listdir(IMAGES_DIR) if f.endswith(".jpeg")])
    if not all_files:
        print("No images found in data/images")
        return
        
    # Pick 3 random or first 3
    selected_files = all_files[:3]
    print(f"Selected images: {selected_files}")
    
    clips = []
    for fname in selected_files:
        path = os.path.join(IMAGES_DIR, fname)
        print(f"Processing {path}...")
        clip = create_infinity_clip(path, DURATION_PER_IMAGE)
        clips.append(clip)
        
    final_video = concatenate_videoclips(clips)
    
    os.makedirs("output", exist_ok=True)
    final_video.write_videofile(OUTPUT_FILE, fps=24)
    print(f"Done! Check {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
