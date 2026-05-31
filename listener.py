# Imports
import neo4j
import pickle
import ollama
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import io
import utilities as utils

driver = utils.driver

FS = 16000
DURATION = 5 
prompt_instruction = """You are an audio processing assistant. Your task is to analyze the provided audio data and give appropriate response. 

"""

# Make it output a JSON. Input the predefined keywords into Modelfile and make new model.

def record_audio():
    print("Recording...")
    audio = sd.rec(int(DURATION * FS), samplerate=FS, channels=1)
    sd.wait()
    print("Recording complete.")
    wav_buffer = io.BytesIO()
    wav.write(wav_buffer, FS, audio)
    return wav_buffer.getvalue()

def initial_llm_processing(audio_data):
    response = ollama.generate(
        model='gemma4b-fixed',
        prompt=prompt_instruction,
        images=[audio_data],  # Multimodal binary buffers are passed through the image/media parameter list
        format='',         # Forces Ollama to constrain vocabulary to valid JSON matrices
        options={
            'temperature': 0.0  # Zero temperature locks down deterministic instruction matching
        }
    )
    print("LLM Raw Response:", response)
    return response['choices'][0]['message']['content']

def listen():
    audio_data = record_audio()
    llm_response = initial_llm_processing(audio_data)
    print("LLM Response:", llm_response)

    return llm_response



