import os
import time
from gtts import gTTS
import playsound

def text_to_speech(text):
    """Convert text to speech and play it."""
    tts = gTTS(text=text, lang="en")
    filename = "output.mp3"
    tts.save(filename)

    # Play the generated speech
    playsound.playsound(filename)

    # Remove the file after playing
    os.remove(filename)

# Example: AI-generated response
# ai_response = "Hello! This is your AI assistant speaking. How can I help you today?"
text_to_speech(ai_response)  # Speak the output
