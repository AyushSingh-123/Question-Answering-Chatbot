import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import queue
import threading

# Initialize the Whisper model
model_size = "large-v3"
model = WhisperModel(model_size, device="cuda", compute_type="float32")

# Parameters for real-time audio capture
SAMPLE_RATE = 16000  # Whisper expects 16 kHz audio
CHUNK_SIZE = 1024 
DURATION = 5   
  # Size of each audio chunk to process

# Create a queue to store transcriptions
transcription_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Callback function to process incoming audio data."""
    if status:
        print(status)
    audio_data = indata[:, 0]  # Extract audio from the first channel
    audio_data = np.float32(audio_data)  # Ensure audio data is float32

    # Run transcription on the audio chunk
    segments, info = model.transcribe(audio_data, beam_size=5)

    # Output detected language and transcription
    detected_language = info.language
    language_probability = info.language_probability
    transcription = []

    for segment in segments:
        transcription.append(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")

    # Put the transcription in the queue
    transcription_queue.put((detected_language, language_probability, transcription))

def transcribe_audio():
    """Thread function to continuously print transcriptions."""
    while True:
        detected_language, language_probability, transcription = transcription_queue.get()
        
        # Print the detected language and its probability
        print(f"\nDetected language: '{detected_language}' with probability: {language_probability:.2f}")
        print("Transcription:")
        print("\n".join(transcription))

def real_time_transcription():
    """Start the audio input stream and transcription thread."""
    # Start the audio stream
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback, blocksize=CHUNK_SIZE):
        print("Listening and transcribing in real-time... Press Ctrl+C to stop.")

        # Start a separate thread for printing transcriptions
        transcription_thread = threading.Thread(target=transcribe_audio, daemon=True)
        transcription_thread.start()

        # Keep the main thread alive to listen for keyboard interrupts
        try:
            while True:
                sd.sleep(1000)
        except KeyboardInterrupt:
            print("Stopping transcription.")

# Start the real-time transcription
if __name__ == "__main__":
    real_time_transcription()