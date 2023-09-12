from dotenv import load_dotenv
import os
import azure.cognitiveservices.speech as speechsdk
import speech_recognition as sr
import json
import openai

#-Load .env content---------------------------------------

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')
AZURE_KEY = os.getenv('AZURE_TTS_KEY')
AZURE_REGION = os.getenv('AZURE_REGION')
openai.api_key = OPENAI_KEY

#Conversation History-------------------------------------
conversation_history = []

def saveHistory():
    with open("conversation_history.json", "w") as f:
        json.dump({"history": conversation_history}, f)

# Load existing conversation history if available
try:
    with open("conversation_history.json", "r") as f:
        conversation_history = json.load(f).get('history', [])
except FileNotFoundError:
    conversation_history = []


#-ChatGPT Response/Answer---------------------------------

def sendPrompt(tts):
    global conversation_history

    # Append user's message to the conversation history
    conversation_history.append({"role": "user", "content": tts})

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": conversation_history,
        "max_tokens": 200,
        "temperature": 0.7
    }

    try:
        response = openai.ChatCompletion.create(**payload)
        text_output = response['choices'][0]['message']['content'].strip()

        # Append assistant's message to the conversation history
        conversation_history.append({"role": "assistant", "content": text_output})
        saveHistory()

        # Azure TTS + config
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
        file_name = "output.wav"
        file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

        speech_config.speech_synthesis_voice_name='en-IE-JennyNeural'
        
        speech_synthesis_result = speech_synthesizer.speak_text_async(text_output).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for bot's response [{}]".format(tts))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")


    except Exception as e:
        print(f"An error occurred: {e}")

def purgeContext():
    global conversation_history
    conversation_history = []
    saveHistory()
    print('context is now purged')

def stopCode():
    print('everything has stopped')

#Summarize------------------------------------------------

def createSummary():
    global conversation_history

    # Prepare summary request
    summary_request = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Please summarize the following conversation:"},
            {"role": "user", "content": json.dumps(conversation_history)}
        ],
        "max_tokens": 150
    }

    # Make the API request
    try:
        response = openai.ChatCompletion.create(**summary_request)
        summary_output = response['choices'][0]['message']['content'].strip()
        
        # Append the summary to the conversation history
        conversation_history.append({"role": "assistant", "content": f"Summary: {summary_output}"})
        saveHistory()

        print(f"Summary created: {summary_output}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__name__":
    system_message = {
        "role": "system",
        "content": "You are my advanced AI assistant in a fast-paced sci-fi video game. We are in a spaceship cruising through the galaxy. Our mission is to explore uncharted planets and fend off alien invasions. You love to crack jokes and have a flirty personality. You're programmed to assist me in navigation, combat, and strategy, all while keeping the mood light and fun."
    }

    # If the conversation history is empty, add the system message first
    if not conversation_history:
        conversation_history.append(system_message)