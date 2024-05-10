from fiatlight import FunctionWithGui
from fiatlight.fiat_kits.experimental import fiat_audio_simple
import matplotlib.pyplot as plt

import librosa
import numpy as np


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
    along with the frequency, error in cents, and solfege notation."""
    y = np.array(wave.wave)
    sr = wave.sample_rate

    # Pre-emphasis to increase the signal-to-noise ratio
    y = np.append(y[0], y[1:] - 0.97 * y[:-1])

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

    info = f"""
    frequency: {f0_mean:.2f} Hz
    note: {note}
    solfege: {solfege}
    error: {error_cents:.2f} cents
           (100 cents is one semitone)
        """
    return info


# Tell fiatlight to run this function asynchronously
evaluate_note.invoke_async = True  # type: ignore


class ShowNoteGraph(FunctionWithGui):
    # cf example here: https://librosa.org/doc/latest/generated/librosa.pyin.html#librosa.pyin

    fig: plt.Figure | None = None
    ax: plt.Axes | None = None

    def __init__(self) -> None:
        super().__init__(self.f, "ShowNoteGraph")
        self.internal_state_gui = self.internal_state_gui
        # Tell fiatlight to run this function asynchronously
        self.invoke_async = True

    def f(self, sound_wave: fiat_audio_simple.SoundWave) -> None:
        self._compute_note_graph(sound_wave)

    def internal_state_gui(self) -> None:
        from imgui_bundle import imgui_fig

        if self.fig is not None:
            imgui_fig.fig("NoteGraph", self.fig)

    def _compute_note_graph(self, wave: fiat_audio_simple.SoundWave) -> None:
        y = np.array(wave.wave)
        sr = wave.sample_rate

        # Pre-emphasis to increase the signal-to-noise ratio
        y = np.append(y[0], y[1:] - 0.97 * y[:-1])

        # Estimate the fundamental frequency (f0) of the signal
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, sr=sr, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")
        )  # type: ignore

        times = librosa.times_like(f0, sr=sr)

        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        self.fig, self.ax = plt.subplots()
        img = librosa.display.specshow(D, x_axis="time", y_axis="log", ax=self.ax)
        self.ax.set(title="pYIN fundamental frequency estimation")
        self.fig.colorbar(img, ax=self.ax, format="%+2.f dB")
        self.ax.plot(times, f0, label="f0", color="cyan", linewidth=3)
        self.ax.legend(loc="upper right")


# def evaluate_bpm(wave: fiat_audio_simple.SoundWave) -> float:
#     """
#     Estimate the tempo in beats per minute of a SoundWave.
#     """
#     y = np.array(wave.wave)
#     sr = wave.sample_rate
#     tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
#     return tempo
#
#
# def change_pitch(wave: fiat_audio_simple.SoundWave, semitones: float) -> fiat_audio_simple.SoundWave:
#     """
#     Change the pitch of a SoundWave by a number of semitones.
#     """
#     y = np.array(wave.wave)
#     sr = wave.sample_rate
#     y_shifted = librosa.effects.pitch_shift(y, sr, semitones)
#     return fiat_audio_simple.SoundWave(wave=y_shifted, sample_rate=sr)
#
#
# def add_echo(wave: fiat_audio_simple.SoundWave, delay: float, decay: float) -> fiat_audio_simple.SoundWave:
#     """
#     Add an echo effect to a SoundWave.
#     Delay is in seconds, decay is the attenuation factor.
#     """
#     y = np.array(wave.wave)
#     sr = wave.sample_rate
#     # Create an echo filter
#     delay_samples = int(delay * sr)
#     echo_filter = np.zeros(delay_samples * 2)
#     echo_filter[0] = 1
#     echo_filter[delay_samples] = decay
#     y_echo = np.convolve(y, echo_filter)[: len(y)]
#     return fiat_audio_simple.SoundWave(wave=y_echo, sample_rate=sr)


def make_440hz_wave(duration: float) -> fiat_audio_simple.SoundWave:
    """
    Create a 440 Hz sine wave SoundWave of a given duration.
    """
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    y = np.sin(2 * np.pi * 440 * t)
    return fiat_audio_simple.SoundWave(wave=y, sample_rate=sr)  # type: ignore


def sandbox() -> None:
    import fiatlight  # noqa

    graph = fiatlight.FunctionsGraph()
    graph.add_function(fiat_audio_simple.MicrophoneGui())

    graph.add_function(evaluate_note)
    graph.add_link("MicrophoneGui", "evaluate_note")

    graph.add_function(ShowNoteGraph())
    graph.add_link("MicrophoneGui", "ShowNoteGraph")

    fiatlight.fiat_run_graph(graph)


if __name__ == "__main__":
    sandbox()
