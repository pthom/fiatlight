# pip install scipy matplotlib sounddevice librosa
# type: ignore

import numpy as np
import sounddevice
import matplotlib.pyplot as plt
import librosa
import librosa.display

from fiatlight.fiat_kits.fiat_implot import FloatMatrix_Dim1


# Constants
SAMPLE_RATE = 44100  # Sample rate


def record_audio(duration=5, sample_rate=SAMPLE_RATE) -> FloatMatrix_Dim1:
    """Record audio from the microphone for a given duration and sample rate."""
    print("Recording...")
    audio = sounddevice.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
    sounddevice.wait()  # Wait until recording is finished
    print("Recording complete.")
    audio_flat = audio.flatten()  # Convert to 1D array
    return audio_flat  # Return as 1D array


def plot_waveform(audio, sample_rate=SAMPLE_RATE):
    """Plot the waveform of the recorded audio."""
    plt.figure(figsize=(10, 4))
    plt.plot(np.linspace(0, len(audio) / sample_rate, len(audio)), audio)
    plt.title("Audio Waveform")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()


def plot_spectrogram(audio, sample_rate=SAMPLE_RATE):
    """Plot the spectrogram of the recorded audio."""
    X = librosa.stft(audio)
    Xdb = librosa.amplitude_to_db(abs(X))
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(Xdb, sr=sample_rate, x_axis="time", y_axis="hz")
    plt.title("Spectrogram")
    plt.colorbar(format="%+2.0f dB")
    plt.show()


def change_pitch(audio, sample_rate=SAMPLE_RATE, n_steps=0):
    """Change the pitch of the audio data."""
    return librosa.effects.pitch_shift(audio, sample_rate, n_steps)


# Example usage
def main_standalone():
    audio = record_audio()
    plot_waveform(audio)
    plot_spectrogram(audio)
    # audio_higher = change_pitch(audio, n_steps=4)  # Raises pitch by 4 semitones
    # plot_waveform(audio_higher)
    # plot_spectrogram(audio_higher)


if __name__ == "__main__":
    main_standalone()
