import numpy as np


def downsample_wave_minmax(wave: np.ndarray, max_samples: int) -> np.ndarray:  # type: ignore
    """Downsample using min/max strategy for plotting.
    Alternates between min and max per chunk, to simulate waveform spikes.
    Only supports 1D arrays (flattened audio channel)."""
    assert wave.ndim == 1
    chunk_size = int(np.ceil(len(wave) / max_samples))
    downsampled = []
    use_min = True

    for i in range(0, len(wave), chunk_size):
        chunk = wave[i : i + chunk_size]
        val = chunk.min() if use_min else chunk.max()
        downsampled.append(val)
        use_min = not use_min

    return np.array(downsampled)
