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
driver = utils.driver

FS = 16000
DURATION = 5 
prompt_instruction = """You are an audio processing assistant. Your task is to analyze the provided audio data and give appropriate response. 

"""


class AudioAnalysis(BaseModel):
    summary: str
    detected_language: str
    action_items: list[str]
    sentiment: str

# Make it output a JSON. Input the predefined keywords into Modelfile and make new model.

def record_audio():
    print("Recording...")
    audio = sd.rec(int(DURATION * FS), samplerate=FS, channels=1)
    sd.wait()
    print("Recording complete.")

    return audio.flatten()

def initial_llm_processing(audio_data):
    audio_model = whisper.load_model("base")
    query = audio_model.transcribe(audio_data)
    prompt = query["text"]

    
    response = ollama.chat(
        model="gemma3n:e4b",
        messages=[
              {
                "role": "user",
                "content": f"Convert the following data into a strict JSON object. DO NOT DO ANY FURTHER PROCESSING. ONLY OUTPUT THE JSON OBJECT DIRECTLY, NO OTHER FLUFF. Get the required info from the following text: {prompt}"
            }
        ],
        options={
            "temperature": 0.0  # Zero temperature locks down deterministic instruction matching
        },
        format=AudioAnalysis.model_json_schema(),
    )
    print("LLM Raw Response:", response)
    return response['message']['content']

def listen():
    audio_data = record_audio()
    llm_response = initial_llm_processing(audio_data)
    print("LLM Response:", llm_response)

    return llm_response



