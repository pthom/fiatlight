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
    return time_ * 15.0


# Interactive sine wave function
def interactive_sine_wave(freq: float, phase: float, amplitude: float):
    x = np.linspace(0, 2 * np.pi, 3000)
    y = amplitude * np.sin(2 * np.pi * freq * x + phase)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_ylim([-1.5, 1.5])
    return fig


# Gaussian heatmap function
def gaussian_heatmap(mean: float, variance: float, colormap: str, levels: int):
    x = y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-((X - mean) ** 2 + (Y - mean) ** 2) / (2 * variance))
    fig, ax = plt.subplots()
    contour = ax.contourf(X, Y, Z, levels, cmap=colormap)
    fig.colorbar(contour, ax=ax)
    return fig


# Data smoothing function
def data_smoothing(window_size: int):
    x = np.linspace(0, 15, 300)
    y = np.sin(x) + np.random.normal(0, 0.1, 300)  # Noisy sine wave
    y_smooth = np.convolve(y, np.ones(window_size) / window_size, mode="same")
    fig, ax = plt.subplots()
    ax.plot(x, y, label="Original")
    ax.plot(x, y_smooth, label="Smoothed")
    ax.legend()
    return fig


# Interactive histogram function
def interactive_histogram(n_bars: int, mu: float, sigma: float, average: float, nb_data: int):
    data = np.random.normal(mu, sigma, nb_data) + average
    bins = np.linspace(np.min(data), np.max(data), n_bars)
    fig, ax = plt.subplots()
    ax.hist(data, bins=bins, color="blue", alpha=0.7)
    return fig


# Streamlit app
st.title("Interactive Data Visualization with Streamlit")

# Sine wave section
st.header("Interactive Sine Wave")
freq = st.slider("Frequency", 0.1, 3.0, 1.0)
phase = st.slider("Phase", -np.pi, np.pi, 0.0)
amplitude = st.slider("Amplitude", 0.1, 2.0, 1.0)
fig1 = interactive_sine_wave(freq, phase, amplitude)
st.pyplot(fig1)

# Gaussian heatmap section
st.header("Gaussian Heatmap")
mean = st.slider("Mean", -5.0, 5.0, 0.0)
variance = st.slider("Variance", 0.1, 5.0, 1.0)
colormap = st.selectbox("Colormap", ["viridis", "plasma", "inferno", "magma", "cividis"])
levels = st.slider("Levels", 1, 20, 10)
fig2 = gaussian_heatmap(mean, variance, colormap, levels)
st.pyplot(fig2)

# Data smoothing section
st.header("Data Smoothing")
window_size = st.slider("Window Size", 1, 40, 5)
fig3 = data_smoothing(window_size)
st.pyplot(fig3)

# Histogram section
st.header("Interactive Histogram")
n_bars = st.slider("Number of Bars", 1, 300, 10)
mu = st.slider("Mean", -5.0, 5.0, 0.0, key="mean_histogram")
sigma = st.slider("Standard Deviation", 0.1, 5.0, 1.0)
average = st.slider("Average", 0.0, 1000.0, 500.0)
nb_data = st.slider("Number of Data Points", 100, 1000000, 1000)
fig4 = interactive_histogram(n_bars, mu, sigma, average, nb_data)
st.pyplot(fig4)
