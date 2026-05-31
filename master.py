# Imports
import neo4j
import pickle
import ollama
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import io
import utilities as utils
import listener
import json
import contextwords as cw



def agent_mode():
    user_input = listener.listen()
    if  json.loads(user_input)['intent'] == "command":
        # process command
        
        pass
    elif json.loads(user_input)['intent'] == "feedback":
        # process feedback
        pass    
    elif json.loads(user_input)['intent'] == "question-general":
        # process general question
        
        pass
    elif json.loads(user_input)['intent'] == "question-specific":
        # process specific question
        pass
    elif json.loads(user_input)['intent'] == "question-general-changing":
        # process general changing question
        pass
    else:
        # handle unknown intent
        pass

def learn_mode_pdf():
    # process PDF files and learn from them
    pass

def learn_mode_text():
    # process text files and learn from them
    pass



def main():
    pass
    # Add a use mode feature where it sees if we want it in agent mode or in learn mode and depending on that, the processing changes. 
    




if __name__ == "__main__":
    main()
