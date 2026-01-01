import os
import json
import time
from pdf_processor import PDFProcessor
from vision_agent import VisionAgent
from audio_generator import AudioGenerator
from video_editor import VideoEditor

def main():
    print("=== Manga Recap Generator (Fully Automated) ===")
    
    pdf_path = input("Enter the path to the Manga PDF: ").strip()
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found.")
        return

    # 1. Extract Images
    processor = PDFProcessor()
    image_paths = processor.extract_images(pdf_path)
    
    # 2. Analyze PDF with Gemini (Full Context)
    vision_agent = VisionAgent()
    audio_gen = AudioGenerator()
    
    print("\nStarting AI Analysis of the PDF...")
    try:
        segments = vision_agent.analyze_pdf(pdf_path)
    except Exception as e:
        print(f"Critical Error during analysis: {e}")
        return

    print(f"\nAnalysis complete. Generated {len(segments)} narrative segments.")

    # 3. Process Segments and Generate Audio
    print("\nGenerating Audio Narration (Per Segment)...")
    audio_dir = "data/audio"
    os.makedirs(audio_dir, exist_ok=True)
    
    batches_data = []
    
    for i, seg in enumerate(segments):
        start_page = seg.get('start_page', 1)
        end_page = seg.get('end_page', 1)
        script = seg.get('script', "")
        style = seg.get('style_instructions', "")
        
        print(f"Processing Segment {i+1}: Pages {start_page}-{end_page}")
        
        # Identify corresponding images (1-based index to 0-based list)
        # Ensure indices are within bounds
        start_idx = max(0, start_page - 1)
        end_idx = min(len(image_paths), end_page)
        
        segment_images = image_paths[start_idx:end_idx]
        
        if not segment_images:
            print(f"Warning: No images found for pages {start_page}-{end_page}")
            continue

        audio_filename = f"segment_{i+1:03d}.wav"
        audio_path = os.path.join(audio_dir, audio_filename)
        
        try:
            audio_gen.generate_audio(
                script_text=script,
                style_text=style,
                output_path=audio_path
            )
            
            # Create batch item
            # We store the segment script in the first item or just carrying it in the batch is enough
            # But specific items structure is expected by VideoEditor to find images
            batch_items = []
            for img in segment_images:
                batch_items.append({
                    "image_path": img,
                    "script": script # redundant but keeps structure
                })
            
            batches_data.append({
                "audio_path": audio_path,
                "items": batch_items,
                "segment_script": script
            })
            
            # Higher delay for TTS API to respect quotas
            time.sleep(5) 
        except Exception as e:
            print(f"Error generating audio for segment {i+1}: {e}")

    # 5. Assemble Video
    if not batches_data:
        print("No audio generated, skipping video assembly.")
        return

    print("\nAssembling Final Video...")
    editor = VideoEditor()
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_name = f"{pdf_name}_recap.mp4"
    
    final_path = editor.create_video(batches_data, output_filename=output_name)
    
    if final_path:
        print(f"\nSUCCESS! Your Manga Recap is ready: {final_path}")

    # Save project state for debugging/reuse
    data_file = "config/recap_project.json"
    recap_data = {"pdf_name": pdf_name, "batches": batches_data}
    with open(data_file, "w") as f:
        json.dump(recap_data, f, indent=4)

if __name__ == "__main__":
    main()
