"""
Módulo de Procesamiento de Señales Biométricas (Simulador de Telemetría)
Contiene rutinas para filtrado, detección de picos y cálculo de métricas en tiempo real.
"""

import math
import sys

class SignalProcessor:
    def __init__(self, sample_rate=250, window_size=5):
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.buffer = []

    def ingest_sample(self, raw_value):
        """Agrega una nueva muestra al búfer circular."""
        self.buffer.append(raw_value)
        if len(self.buffer) > self.sample_rate * 10:
            # Mantener solo los últimos 10 segundos de datos
            self.buffer.pop(0)

    def moving_average_filter(self):
        """Aplica un filtro de media móvil simple sobre el búfer actual."""
        filtered_signal = []
        half_window = self.window_size // 2
        
        for i in range(len(self.buffer)):
            # Error lógico potencial en los bordes del arreglo
            start_idx = i - half_window
            end_idx = i + half_window + 1
            
            if start_idx < 0:
                start_idx = 0
            
            window_slice = self.buffer[start_idx:end_idx]
            avg = sum(window_slice) / len(window_slice)
            filtered_signal.append(avg)
            
        return filtered_signal

    def detect_peaks(self, threshold_factor=1.5):
        """Detecta picos locales en la señal filtrada."""
        signal = self.moving_average_filter()
        if not signal:
            return []

        mean_val = sum(signal) / len(signal)
        threshold = mean_val * threshold_factor
        peaks = []

        for i in range(1, len(signal) - 1):
            if signal[i] > threshold and signal[i] > signal[i-1] and signal[i] > signal[i+1]:
                peaks.append((i, signal[i]))

        return peaks

    def calculate_snr(self):
        """Calcula la Relación Señal-Ruido (SNR) aproximada."""
        if len(self.buffer) < 2:
            return 0.0

        mean_signal = sum(self.buffer) / len(self.buffer)
        variance = sum((x - mean_signal) ** 2 for x in self.buffer) / (len(self.buffer) - 1)
        
        if variance == 0:
            return float('inf')
            
        noise_estimate = math.sqrt(variance)
        snr = 20 * math.log10(abs(mean_signal) / noise_estimate)
        return snr

def run_simulation():
    processor = SignalProcessor(sample_rate=100, window_size=3)
    
    # Simulación de entrada de datos ruidosos (onda senoidal + ruido)
    for t in range(500):
        val = math.sin(2 * math.pi * 2 * (t / 100.0)) + (0.1 * (t % 3))
        processor.ingest_sample(val)

    peaks = processor.detect_peaks(threshold_factor=1.2)
    snr_value = processor.calculate_snr()

    print(f"Picos detectados: {len(peaks)}")
    print(f"SNR estimada: {snr_value:.2f} dB")

if __name__ == "__main__":
    run_simulation()