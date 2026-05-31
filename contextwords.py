intent_types = {
    "question-general": "A general question that can be answered with common knowledge or information that is widely available. This type of question does not require access to personal data or specific files. And is likely present in the Common Sense Knowledge Base.",

    "question-specific": "A specific question that requires access to personal data or specific files that the world doesn't know about. Or, is an obscure fact that Common Sense Knowledge Base does not contain. This type of question has a specific answer that doesn't change with time.",   

    "question-general-changing": "A general question that can be answered with common knowledge or information that changes with time. This type of question requires access to up-to-date information.",

    "feedback": "Feedback from the user about the system's performance, which can be used to improve the system.",

    "command": "A command from the user that instructs the system to perform a specific action or task."
}

tone_types = {
    "angry": "The user is expressing anger or frustration. The response should be empathetic and attempt to de-escalate the situation.",

    "sad": "The user is expressing sadness or disappointment. The response should be supportive and comforting.",

    "happy": "The user is expressing happiness or excitement. The response should be positive and uplifting.",

    "neutral": "The user is expressing a neutral tone. The response should be informative and straightforward.",

    "serious": "The user is expressing a serious tone. The response should be formal and respectful and factually accurate."

}

# expected user input in a JSON format:
    # {
    #     intent: "question", # question-general, feedback, command, question-specific, question-general-changing, etc... ( Question-general-changing is for things like weather and all that can change with time. Question-specific is for things that is specific to this user's personal data/files that the world doesn't know about that have a specific answer that doesn't change with time. )
    #     
    #     phrase: "What is the weather like today?",
    #     keyword: "smtn", # most important word in the phrase that gives the most context about the user's intent. In this case, it would be "weather". This will be used to query the database for relevant information and also to determine which model to use for processing the user's request.
    #     generative_tag: Y/N, # whether the response requires generative capabilities or not. This will be used to determine which model to use for processing the user's request.
    #     tone: "angry", # the tone of the user's voice. This will be used to determine the tone of the response and also to determine which model to use for processing the user's request.
    #     # more fields can be added as needed, such as sentiment, emotion, etc
    # } 

# Relations:
"""
/r/IsA
/r/DefinedAs
/r/HasContext
/r/HasProperty
/r/RelatedTo
/r/SimilarTo
/r/Antonym
/r/Synonym
/r/FormOf
/r/AtLocation
/r/DerivedFrom
/r/EtymologicallyRelatedTo
/r/CapableOf
/r/InstanceOf
/r/dbpedia/genre
/r/PartOf
/r/MadeOf
/r/ReceivesAction
/r/HasA
/r/UsedFor
/r/NotHasProperty
/r/CausesDesire
/r/dbpedia/language
/r/dbpedia/occupation
/r/HasSubevent
/r/LocatedNear
/r/dbpedia/influencedBy
/r/DistinctFrom
/r/MannerOf
mw:MayHaveProperty
fn:HasLexicalUnit
/r/Entails
/r/dbpedia/field
/r/dbpedia/genus
/r/HasPrerequisite
/r/dbpedia/capital
/r/dbpedia/leader
/r/CreatedBy
/r/Causes
/r/NotCapableOf
/r/NotDesires
/r/dbpedia/product
/r/Desires
/r/MotivatedByGoal
/r/HasFirstSubevent
/r/HasLastSubevent
/r/EtymologicallyDerivedFrom
/r/dbpedia/knownFor
/r/SymbolOf
at:xAttr
at:xEffect
at:xIntent
at:xReact
at:xWant
at:oReact
at:oWant
at:xNeed
at:oEffect
"""
