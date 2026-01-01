import os
import mimetypes
import struct
import dotenv
from google import genai
from google.genai import types

dotenv.load_dotenv()

class AudioGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.5-flash-preview-tts"

    def generate_audio(self, script_text: str, style_text: str, output_path: str, voice_name: str = "Achird", max_retries: int = 3):
        """
        Generates audio for a given script and style, and saves it to output_path.
        """
        print(f"Generating audio for script: {script_text[:50]}...")
        
        prompt = f"STYLE: {style_text}\n\nTEXT TO SPEAK: {script_text}"
        
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            ),
        )

        for attempt in range(max_retries):
            try:
                audio_data = b""
                mime_type = "audio/wav" # Default

                for chunk in self.client.models.generate_content_stream(
                    model=self.model_id,
                    contents=prompt,
                    config=generate_content_config,
                ):
                    if (chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts):
                        part = chunk.candidates[0].content.parts[0]
                        if part.inline_data:
                            audio_data += part.inline_data.data
                            if part.inline_data.mime_type:
                                mime_type = part.inline_data.mime_type

                if not audio_data:
                    raise Exception("No audio data received from Gemini")

                # Handle WAV header if needed
                if "audio/L16" in mime_type or not output_path.endswith(".wav"):
                    final_data = self._convert_to_wav(audio_data, mime_type)
                else:
                    final_data = audio_data

                with open(output_path, "wb") as f:
                    f.write(final_data)
                
                print(f"Audio saved to: {output_path}")
                return output_path

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    wait_time = 10 * (attempt + 1) # Exponential backoff
                    print(f"\nQuota exceeded for audio. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                    import time
                    time.sleep(wait_time)
                else:
                    raise e
        
        raise Exception(f"Failed to generate audio after {max_retries} attempts.")

    def _convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        parameters = self._parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            chunk_size,
            b"WAVE",
            b"fmt ",
            16,
            1,
            num_channels,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
            b"data",
            data_size
        )
        return header + audio_data

    def _parse_audio_mime_type(self, mime_type: str) -> dict:
        bits_per_sample = 16
        rate = 24000
        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate = int(param.split("=", 1)[1])
                except: pass
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except: pass
        return {"bits_per_sample": bits_per_sample, "rate": rate}

if __name__ == "__main__":
    # Test
    gen = AudioGenerator()
    gen.generate_audio("Hello world", "Cheerful", "output/test.wav")
