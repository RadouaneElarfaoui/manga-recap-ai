import os
import json
from video_editor import VideoEditor

def assemble():
    print("=== Manga Recap Assembler ===")
    
    data_file = "config/recap_project.json"
    if not os.path.exists(data_file):
        print(f"Error: Project data file {data_file} not found. Run analysis first.")
        return

    with open(data_file, "r") as f:
        project_data = json.load(f)

    audio_dir = input("Enter the directory path containing your downloaded MP3 files: ").strip()
    if not os.path.isdir(audio_dir):
        print(f"Error: Directory {audio_dir} not found.")
        return

    # Match audio files to clips
    # We assume the user saved them as page_001.mp3, page_002.mp3 etc.
    # Or we can look for files that match the image order.
    
    audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith(".mp3")])
    
    if len(audio_files) < len(project_data['clips']):
        print(f"Warning: Found only {len(audio_files)} audio files for {len(project_data['clips'])} clips.")
    
    assembly_data = []
    for i, clip in enumerate(project_data['clips']):
        if i < len(audio_files):
            clip['audio_path'] = os.path.join(audio_dir, audio_files[i])
            assembly_data.append(clip)
        else:
            print(f"Missing audio for {clip['image_path']}")

    if not assembly_data:
        print("No clips to assemble.")
        return

    editor = VideoEditor()
    output_name = f"{project_data['pdf_name']}_recap.mp4"
    editor.create_video(assembly_data, output_filename=output_name)

if __name__ == "__main__":
    assemble()
