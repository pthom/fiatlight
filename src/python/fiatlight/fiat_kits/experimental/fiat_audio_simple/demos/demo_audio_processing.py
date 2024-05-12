# pip install librosa matplotlib numpy scipy pedalboard

from fiatlight import FunctionWithGui
from fiatlight.fiat_kits.experimental import fiat_audio_simple
from imgui_bundle import hello_imgui, imgui_fig, ImVec2
from fiatlight.fiat_types import Float_0_1
import matplotlib.pyplot as plt

import librosa
import numpy as np

PRE_EMPHASIS_FACTOR = 0.97


def set_pre_emphasis_factor(factor: Float_0_1 = 0.97) -> None:
    """Set the pre-emphasis factor for the pre-emphasis filter. Good values are between 0.9 and 0.97.
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
tempo: {tempo:.2f} BPM
        """
    return info


# Tell fiatlight to run this function asynchronously
evaluate_note.invoke_async = True  # type: ignore


class ShowFundamentalFreqGraph(FunctionWithGui):
    # cf example here: https://librosa.org/doc/latest/generated/librosa.pyin.html#librosa.pyin

    # A matplotlib figure and axis to display the note graph
    fig: plt.Figure | None = None
    fig_size: ImVec2 | None = None
    should_refresh_fig: bool = False

    def __init__(self) -> None:
        super().__init__(self.f, "ShowFundamentalFreqGraph")
        # Our internal state GUI function will display the matplotlib figure
        self.internal_state_gui = self.internal_state_gui
        # Tell fiatlight to run this function asynchronously
        self.invoke_async = True
        # Save internal Gui option
        self.save_internal_gui_options_to_json = self.save_internal_gui_options_to_json
        self.load_internal_gui_options_from_json = self.load_internal_gui_options_from_json

    def save_internal_gui_options_to_json(self) -> dict:
        return {"fig_size": self.fig_size.to_dict()}

    def load_internal_gui_options_from_json(self, options: dict) -> None:
        if "fig_size" in options:
            self.fig_size = ImVec2.from_dict(options["fig_size"])

    def f(self, sound_wave: fiat_audio_simple.SoundWave) -> None:
        self._compute_note_graph(sound_wave)

    def internal_state_gui(self) -> None:
        if self.fig is None:
            return

        if self.fig_size is None:
            self.fig_size = hello_imgui.em_to_vec2(20, 20)

        imgui_fig.fig("##NoteGraph", self.fig, self.fig_size, refresh_image=self.should_refresh_fig)
        self.should_refresh_fig = False

    def _compute_note_graph(self, wave: fiat_audio_simple.SoundWave) -> None:
        wave = apply_pre_emphasis_filter(wave)

        # this function will be called asynchronously!
        # (see self.invoke_async = True in __init__)
        y = np.array(wave.wave)
        sr = wave.sample_rate

        # Estimate the fundamental frequency (f0) of the signal
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, sr=sr, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")
        )  # type: ignore

        times = librosa.times_like(f0, sr=sr)
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)

        # Since this function is async, we shall not fill self.fig until it is fully ready
        # Instead we work on a local fig
        fig, ax = plt.subplots()
        img = librosa.display.specshow(D, x_axis="time", y_axis="log", ax=ax)
        ax.set(title="pYIN fundamental frequency estimation")
        fig.colorbar(img, ax=ax, format="%+2.f dB")
        ax.plot(times, f0, label="f0", color="cyan", linewidth=3)
        ax.legend(loc="upper right")

        # And copy it atomically when it is ready
        self.fig = fig
        self.should_refresh_fig = True


class ShowHarmonicPercussiveGraph(FunctionWithGui):
    fig: plt.Figure | None = None
    fig_size: ImVec2 | None = None
    should_refresh_fig: bool = False

    def __init__(self) -> None:
        super().__init__(self.f, "ShowHarmonicPercussiveGraph")
        self.internal_state_gui = self.internal_state_gui
        self.invoke_async = True

    def f(self, sound_wave: fiat_audio_simple.SoundWave) -> None:
        self._compute_graph(sound_wave)

    def internal_state_gui(self) -> None:
        if self.fig is None:
            return

        if self.fig_size is None:
            self.fig_size = hello_imgui.em_to_vec2(20, 20)

        imgui_fig.fig("##OnsetGraph", self.fig, self.fig_size, refresh_image=self.should_refresh_fig)
        self.should_refresh_fig = False

    def _compute_graph(self, wave: fiat_audio_simple.SoundWave) -> None:
        wave = apply_pre_emphasis_filter(wave)

        y = wave.wave
        sr = wave.sample_rate

        # Load audio file
        # y, sr = librosa.load(librosa.ex("choice"), duration=10)

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

        self.fig = fig
        self.should_refresh_fig = True


def add_chorus_effect(wave: fiat_audio_simple.SoundWave) -> fiat_audio_simple.SoundWave:
    from pedalboard import Pedalboard, Chorus, Reverb

    # Make a Pedalboard object, containing multiple audio plugins:
    board = Pedalboard([Chorus(), Reverb(room_size=0.25)])

    # Run the audio through our pedalboard:
    effected = board(wave.wave, wave.sample_rate, reset=False)

    return fiat_audio_simple.SoundWave(wave=effected, sample_rate=wave.sample_rate)  # type: ignore


add_chorus_effect.invoke_async = True  # type: ignore


def sandbox() -> None:
    import fiatlight  # noqa

    graph = fiatlight.FunctionsGraph()

    graph.add_function(set_pre_emphasis_factor)

    graph.add_function(fiat_audio_simple.MicrophoneGui())

    graph.add_function(evaluate_note)
    graph.add_link("MicrophoneGui", "evaluate_note")

    graph.add_function(ShowFundamentalFreqGraph())
    graph.add_link("MicrophoneGui", "ShowFundamentalFreqGraph")

    graph.add_function(ShowHarmonicPercussiveGraph())
    graph.add_link("MicrophoneGui", "ShowHarmonicPercussiveGraph")

    graph.add_function(add_chorus_effect)
    graph.add_link("MicrophoneGui", "add_chorus_effect")

    fiatlight.fiat_run_graph(graph)


if __name__ == "__main__":
    sandbox()
