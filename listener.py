# Imports
import neo4j
import pickle
import ollama
import sounddevice as sd
import whisper
import numpy as np
import scipy.io.wavfile as wav
import io
import utilities as utils
from pydantic import BaseModel
#import soundfile as sf
from gtts import gTTS
import pygame
import os
from kokoro import KPipeline

pipeline = KPipeline(lang_code='b')

driver = utils.driver

FS = 16000
DURATION = 8
prompt_instruction = ""
sd.default.device = (None, 10)

class AudioAnalysis(BaseModel):
    intent: str
    keyword: str
    phrase: str
    sentiment: str

# Make it output a JSON. Input the predefined keywords into Modelfile and make new model.

def record_audio():
    print("Recording...")
    audio = audio = sd.rec(int(DURATION * FS), samplerate=FS, channels=1, dtype="float32")
    sd.wait()
    print("Recording complete.")

    return audio.flatten()

def initial_llm_processing(audio_data):
    audio_model = whisper.load_model("base")
    query = audio_model.transcribe(audio_data)
    prompt = query["text"]

    
    response = ollama.chat(
        model="json-translator",
        messages=[
              {
                "role": "user",
                "content": f"Convert the following data into a strict JSON object. DO NOT DO ANY FURTHER PROCESSING. ONLY OUTPUT THE JSON OBJECT DIRECTLY, NO OTHER FLUFF. And the Phrase should be a string. Get the required info from the following text: {prompt}"
            }
        ],
        options={
            "temperature": 0.0  # Zero temperature locks down deterministic instruction matching
        },
        format=AudioAnalysis.model_json_schema(),
        keep_alive=0
    )
    print("LLM Raw Response:", response)
    return response['message']['content']

def listen():
    audio_data = record_audio()
    llm_response = initial_llm_processing(audio_data)
    print("LLM Response:", llm_response)

    return llm_response

"""
def talk(text):
    print("Talking.......")
    print(sd.query_devices())
    print("Default Output Device ID:", sd.default.device[1])
    generator = pipeline(text, voice='af_heart', speed=1.0)
    
    for graphemes, phonemes, audio in generator:
        # Ensure the audio is a float32 array (standard for sounddevice)
        audio_data = np.array(audio, dtype=np.float32)
        
        # Play it back explicitly passing the sample rate (usually 24000 for Kokoro)
        # Ensure FS matches Kokoro's native output (24000 Hz)
        sd.play(audio_data, samplerate=24000, blocking=True)

import sounddevice as sd

for index, device in enumerate(sd.query_devices()):
    # Only show devices that can actually play sound (max_output_channels > 0)
    if device['max_output_channels'] > 0:
        print(f"Index {index}: {device['name']} (Outputs: {device['max_output_channels']})")
"""
def talk(text):
    print("Talking (Google)...")
    # Generate the audio file
    tts = gTTS(text=text, lang='en', tld='com')
    tts.save("speech.mp3")
    
    # Play back via pygame mixer (handles MP3 encoding natively)
    pygame.mixer.init()
    pygame.mixer.music.load("speech.mp3")
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
        
    pygame.mixer.quit()
    os.remove("speech.mp3") # Clean up workspace


