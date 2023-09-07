from dotenv import load_dotenv

import os
import azure.cognitiveservices.speech as speechsdk

import speech_recognition as sr

#-Load .env content---------------------------------------

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')
AZURE_KEY = os.getenv('AZURE_TTS_KEY')
AZURE_REGION = os.getenv('AZURE_REGION')

#-Azure config--------------------------------------------

speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
file_name = "output.wav"
file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

speech_config.speech_synthesis_voice_name='en-IE-JennyNeural'

#---------------------------------------------------------


def sendPrompt(userInput):
    print(userInput)
    speech_synthesis_result = speech_synthesizer.speak_text_async(userInput).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(userInput))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

def purgeContext():
    print('context is purged')

def createSummary():
    print('summary was created')

def stopCode():
    print('everything has stopped')