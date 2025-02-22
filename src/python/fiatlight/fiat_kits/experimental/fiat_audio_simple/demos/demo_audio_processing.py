# type: ignore
"""A demo where you can sing into the microphone and see information about the note you're singing + advanced graphs using librosa
- The frequency of the note
- The note name
- The note name in solfege
- The error in cents (100 cents is one semitone)
- The tempo of the song
"""

# pip install librosa matplotlib numpy scipy pedalboard

# Important:
# in order to display matplotlib figures in our GUI, we need to change matplotlib renderer to Agg,
# before importing pyplot.
import matplotlib

matplotlib.use("Agg")

from fiatlight.fiat_kits.experimental import fiat_audio_simple
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import librosa
import numpy as np

PRE_EMPHASIS_FACTOR = 0.97


def set_pre_emphasis_factor(factor: float = 0.97) -> None:
    """Signal from the microphone needs to be pre-emphasized: good values are between 0.9 and 0.97.
    This will be applied to all functions in this demo."""
    global PRE_EMPHASIS_FACTOR
    PRE_EMPHASIS_FACTOR = factor


def apply_pre_emphasis_filter(wave: fiat_audio_simple.SoundWave) -> fiat_audio_simple.SoundWave:
    """Apply a pre-emphasis filter to the input wave."""
    y = np.array(wave.wave)
    y = np.append(y[0], y[1:] - PRE_EMPHASIS_FACTOR * y[:-1])
    return fiat_audio_simple.SoundWave(wave=y, sample_rate=wave.sample_rate)  # type: ignore


def convert_accidental_to_ascii(note: str) -> str:
    """Convert a note with an accidental to an ASCII representation."""
    # accidental_map = {"#": " sharp", "b": " flat"}
    # base_note = note[0]
    # accidental = note[1:] if len(note) > 1 else ""
    # return f"{base_note} {accidental_map.get(accidental, '')}"
    r = note
    r = r.replace("♯", "#")
    r = r.replace("♭", "b")
    return r


def note_to_solfege(note: str) -> str:
    """Not everyone understands lettered notes, so let's convert them to solfege,
    aka do-re-mi-fa-sol-la-si-do (in Latin countries)

    Note: some would say that "si" should be "ti". There are almost as many ways to say
          the notes as there are key chords. I'll do what I want here.
    """
    conversion_map = {"C": "Do", "D": "Re", "E": "Mi", "F": "Fa", "G": "Sol", "A": "La", "B": "Si"}
    # Handle sharp and flat notes
    base_note = note[0]  # Get the letter part
    accidental = note[1:]  # Get the rest, which could be # or b or empty

    # Convert base note and reattach the accidental
    return conversion_map.get(base_note, base_note) + accidental


def evaluate_note(wave: fiat_audio_simple.SoundWave) -> str:
    """Given a short SoundWave, return textual information about the note played,
    along with the frequency, error in cents, and solfege notation + tempo."""
    wave = apply_pre_emphasis_filter(wave)

    y = np.array(wave.wave)
    sr = wave.sample_rate

    # Estimate the fundamental frequency (f0) of the signal
    f0, voiced_flag, voiced_probs = librosa.pyin(y, sr=sr, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"))  # type: ignore
    # Compute the mean of f0 according to the voiced_probs and voiced_flag
    f0_mean = np.mean(f0[voiced_flag > 0])

    if np.isnan(f0_mean) or f0_mean <= 0:
        return "No note detected."

    # Convert frequency to musical note
    note = librosa.hz_to_note(f0_mean)
    note = convert_accidental_to_ascii(note)
    # Convert note to solfege (this function needs to be defined as shown earlier)
    solfege = note_to_solfege(note)

    # First, convert the note to a frequency
    note_freq = librosa.note_to_hz(note)
    # Compute the error in cents
    error_cents = 1200 * np.log2(f0_mean / note_freq)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    info = f"""frequency: {f0_mean:.2f} Hz
note: {note}
solfege: {solfege}
error: {error_cents:.2f} cents (100 cents is one semitone)
tempo: {tempo[0]:.2f} BPM
        """
    return info


def show_fundamental_freq_graph(wave: fiat_audio_simple.SoundWave) -> Figure:
    # cf example here: https://librosa.org/doc/latest/generated/librosa.pyin.html#librosa.pyin
    wave = apply_pre_emphasis_filter(wave)
    y = np.array(wave.wave)
    sr = wave.sample_rate

    # Estimate the fundamental frequency (f0) of the signal
    f0, voiced_flag, voiced_probs = librosa.pyin(y, sr=sr, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"))  # type: ignore
    times = librosa.times_like(f0, sr=sr)
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    fig, ax = plt.subplots()
    img = librosa.display.specshow(D, x_axis="time", y_axis="log", ax=ax)
    ax.set(title="pYIN fundamental frequency estimation")
    fig.colorbar(img, ax=ax, format="%+2.f dB")
    ax.plot(times, f0, label="f0", color="cyan", linewidth=3)
    ax.legend(loc="upper right")

    return fig


def show_harmonic_percussive_graph(wave: fiat_audio_simple.SoundWave) -> Figure:
    wave = apply_pre_emphasis_filter(wave)
    y = wave.wave
    sr = wave.sample_rate
    # Perform harmonic-percussive source separation
    y_harm, y_perc = librosa.effects.hpss(y)
    # Create a figure with a single subplot
    fig, ax = plt.subplots(figsize=(10, 4))
    # Plot harmonic component
    librosa.display.waveshow(y_harm, sr=sr, alpha=0.5, color="b", ax=ax, label="Harmonic")
    # Plot percussive component
    librosa.display.waveshow(y_perc, sr=sr, color="r", alpha=0.5, ax=ax, label="Percussive")
    # Set title and legend
    ax.set(title="Multiple waveforms")
    ax.legend()

    return fig


def main() -> None:
    import fiatlight as fl

    # Tell fiatlight to run this function asynchronously
    evaluate_note.invoke_async = True  # type: ignore
    show_fundamental_freq_graph.invoke_async = True  # type: ignore
    show_harmonic_percussive_graph.invoke_async = True  # type: ignore

    # Tell fiatlight to display a slider for the pre-emphasis factor with a range from 0.8 to 0.99
    set_pre_emphasis_factor.factor__range = (0.8, 0.99)  # type: ignore

    graph = fl.FunctionsGraph()
    graph.add_function(set_pre_emphasis_factor)
    graph.add_function(fiat_audio_simple.MicrophoneGui())
    graph.add_function(evaluate_note)
    graph.add_function(show_fundamental_freq_graph)
    graph.add_function(show_harmonic_percussive_graph)

    graph.add_link("MicrophoneGui", "evaluate_note")
    graph.add_link("MicrophoneGui", "show_fundamental_freq_graph")
    graph.add_link("MicrophoneGui", "show_harmonic_percussive_graph")

    fl.run(graph, app_name="demo_audio_processing")


if __name__ == "__main__":
    main()
