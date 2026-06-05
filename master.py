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

def determine_mode(intent):
    if intent in ["command", "feedback", "question-general", "question-specific", "question-general-changing"]:
        if intent == "command":
            return "command_mode"
        elif intent == "feedback":
            return "feedback_mode"
        elif intent == "question-general":
            return "question_general_mode"
        elif intent == "question-mode":
            return "question_specific_mode"
        elif intent == "question-mode":
            return "question_general_changing_mode"
    elif intent in ["learn-pdf"]:
        return "learn_mode_pdf"
    elif intent in ["learn-text"]:
        return "learn_mode_text"
    else:
        return "unknown_mode"

    



def main():
    #Greeting and mode selection
    print("Welcome to Project Stark")
    run_flag = True
    while run_flag:
        query = listener.listen()
        print("Received query:", query)
        intent = json.loads(query).get('intent')
        mode = determine_mode(intent)
        print(f"Determined mode: {mode}")
        if mode == "command-mode":
            # process command
            pass
        elif mode == "feedback-mode":
            # process feedback
            pass
        elif mode == "question-mode":
            answer_retuened = answer.answer(json.loads(query))

    pass
    # Add a use mode feature where it sees if we want it in agent mode or in learn mode and depending on that, the processing changes. 
    




if __name__ == "__main__":
    main()
