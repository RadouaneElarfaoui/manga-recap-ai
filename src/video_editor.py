import os
import math
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, ColorClip, VideoFileClip
from moviepy.video.fx import FadeIn
from typing import List, Tuple

class VideoEditor:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.screen_size = (1920, 1080)

    def create_video(self, batches: List[dict], output_filename: str = "final_recap.mp4"):
        """
        batches: List of dictionaries, each containing:
            - 'audio_path': path to a single audio file for the whole batch
            - 'items': List of dictionaries, each with:
                - 'image_path': path to image
                - 'script': text used for word counting
        """
        video_clips = []
        
        for batch in batches:
            aud_path = batch['audio_path']
            items = batch['items']
            
            if not os.path.exists(aud_path):
                print(f"Warning: Skipping batch, missing audio: {aud_path}")
                continue

            # Load full audio
            full_audio = AudioFileClip(aud_path)
            total_duration = full_audio.duration
            
            # Equal distribution of duration
            num_images = len(items)
            if num_images == 0:
                continue
                
            clip_duration = total_duration / num_images
            
            # Start time for audio sub-clips
            current_time = 0
            
            for i, item in enumerate(items):
                img_path = item['image_path']
                if not os.path.exists(img_path):
                    continue
                
                # Extract audio part
                sub_audio = full_audio.subclipped(current_time, current_time + clip_duration)
                current_time += clip_duration

                # Create Cinematic Clip
                clip = self._create_cinematic_clip(img_path, clip_duration)
                clip = clip.with_audio(sub_audio)
                
                # Apply FadeIn to the composite clip
                clip = clip.with_effects([FadeIn(0.5)])
                
                video_clips.append(clip)

        if not video_clips:
            print("No clips to assemble!")
            return None

        print(f"Finalizing video assembly with {len(video_clips)} clips...")
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        output_path = os.path.join(self.output_dir, output_filename)
        # Using preset='fast' to speed up render slightly
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", preset="fast")
        
        print(f"Video saved to: {output_path}")
        return output_path

    def _create_cinematic_clip(self, image_path: str, duration: float):
        img = ImageClip(image_path)
        img_w, img_h = img.size
        screen_w, screen_h = self.screen_size
        
        # --- BACKGROUND (Blurred & Filling Screen) ---
        ratio_bg = max(screen_w / img_w, screen_h / img_h)
        bg_w = int(img_w * ratio_bg)
        bg_h = int(img_h * ratio_bg)
        
        bg = img.resized((bg_w, bg_h))
        
        # Center Crop BG
        x_center, y_center = bg_w / 2, bg_h / 2
        x1 = x_center - screen_w / 2
        y1 = y_center - screen_h / 2
        bg = bg.cropped(x1=x1, y1=y1, width=screen_w, height=screen_h)

        # Darken Background
        bg = bg.with_opacity(0.3)
        
        # --- FOREGROUND (Main Image, Fit Height + Infinity Move) ---
        ratio_fg = min(screen_w / img_w, screen_h / img_h)
        final_ratio_fg = ratio_fg * 1.10 # 10% margin for movement
        
        new_w = int(img_w * final_ratio_fg)
        new_h = int(img_h * final_ratio_fg)
        
        fg = img.resized((new_w, new_h))
        
        center_x, center_y = screen_w / 2, screen_h / 2
        
        def infinity_movement(t):
            u = (2 * math.pi * t) / duration
            A_x = 80
            A_y = 40
            x = A_x * math.sin(u)
            y = A_y * math.sin(2 * u)
            return x, y

        def pos_func(t):
            dx, dy = infinity_movement(t)
            return (center_x - new_w/2 + dx, center_y - new_h/2 + dy)
        
        fg = fg.with_position(pos_func).with_duration(duration)
        bg = bg.with_duration(duration)
        
        base = ColorClip(size=self.screen_size, color=(0,0,0), duration=duration)
        return CompositeVideoClip([base, bg, fg], size=self.screen_size)

if __name__ == "__main__":
    # Test block
    pass
