# type: ignore
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# Initialize the start time
_start_time = time.time()


# Function to get time in seconds
def time_seconds() -> float:
    return time.time() - _start_time


# Function to calculate phase from time
def phase_from_time_seconds(time_: float) -> float:
    return time_ * 2 * np.pi


# Interactive sine wave function
def interactive_sine_wave(freq: float, phase: float, amplitude: float):
    x = np.linspace(0, 2 * np.pi, 3000)
    y = amplitude * np.sin(2 * np.pi * freq * x + phase)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_ylim([-1.5, 1.5])
    return fig


# Streamlit app
st.title("Interactive Animated Sine Wave with Streamlit")

# Sine wave section
st.header("Interactive Sine Wave")
freq = st.slider("Frequency", 0.1, 3.0, 1.0, key="freq")
amplitude = st.slider("Amplitude", 0.1, 2.0, 1.0, key="amplitude")

# Create a placeholder for the plot
plot_placeholder = st.empty()

# Add start and stop buttons with unique keys
if st.button("Start Animation", key="start_button"):
    st.session_state["running"] = True
if st.button("Stop Animation", key="stop_button"):
    st.session_state["running"] = False

# Initialize the running state if not set
if "running" not in st.session_state:
    st.session_state["running"] = False

# Animation loop
while st.session_state["running"]:
    current_time = time_seconds()
    phase = phase_from_time_seconds(current_time)
    fig = interactive_sine_wave(freq, phase, amplitude)
    plot_placeholder.pyplot(fig)
    time.sleep(0.1)  # Update the plot every 0.1 seconds
    if not st.session_state["running"]:
        break

# Display the initial sine wave if animation is not running
if not st.session_state["running"]:
    initial_phase = phase_from_time_seconds(time_seconds())
    fig = interactive_sine_wave(freq, initial_phase, amplitude)
    plot_placeholder.pyplot(fig)
