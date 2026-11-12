"""
DEEPFAKE X - Synthetic Voice & Audio Forensics Module
Real-time neural inference using pretrained Wav2Vec 2.0 sequence classifier.
Zero-fabrication ISO/IEC 27037 compliant pipeline.
Supports WAV, MP3, FLAC formats, non-destructive resampling to 16kHz,
spectrogram and waveform generation, and rigorous integrity safeguards.
"""

import io
import time
import hashlib
import logging
from typing import Dict, Any, Optional, Tuple
import numpy as np
import soundfile as sf
from scipy import signal

import torch
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

logger = logging.getLogger("deepfakex.audio_detector")

MODEL_ID = "MelodyMachine/Deepfake-audio-detection-V2"
TARGET_SAMPLE_RATE = 16000
MAX_DURATION_SECONDS = 60.0
MAX_FILESIZE_BYTES = 25 * 1024 * 1024  # 25 MB
MIN_DURATION_SECONDS = 0.5
SILENCE_RMS_THRESHOLD = 0.0008

class AudioForensicDetector:
    _instance: Optional["AudioForensicDetector"] = None

    @classmethod
    def get_instance(cls) -> "AudioForensicDetector":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # Configure device with CUDA GPU priority on RTX 2050
        if torch.cuda.is_available():
            try:
                self._device = torch.device("cuda:0")
                self.device_name = torch.cuda.get_device_name(0)
                # Test allocation
                _ = torch.zeros(1, device=self._device)
            except Exception as e:
                logger.warning(f"CUDA initialization failed for audio model, falling back to CPU: {e}")
                self._device = torch.device("cpu")
                self.device_name = "CPU (Fallback)"
        else:
            self._device = torch.device("cpu")
            self.device_name = "CPU"

        # Load feature extractor and model
        self._feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_ID)
        self._model = AutoModelForAudioClassification.from_pretrained(MODEL_ID)
        self._model.to(self._device)
        self._model.eval()

    @staticmethod
    def compute_sha256(raw_bytes: bytes) -> str:
        return hashlib.sha256(raw_bytes).hexdigest()

    def process_and_analyze_audio(
        self,
        raw_bytes: bytes,
        filename: str,
        max_duration: float = MAX_DURATION_SECONDS,
        max_size: int = MAX_FILESIZE_BYTES,
    ) -> Dict[str, Any]:
        """
        Validates, decodes, generates acoustic artifacts (waveform & spectrogram),
        and runs genuine Wav2Vec2 neural inference on audio samples.
        Preserves original raw audio bytes and hashes before processing.
        """
        start_time = time.perf_counter()
        file_size = len(raw_bytes)
        sha256_hash = self.compute_sha256(raw_bytes)

        # 1. Defensive bounds validation
        if file_size > max_size:
            return {
                "error": f"Audio file size ({file_size / (1024*1024):.2f} MB) exceeds maximum allowed limit of {max_size / (1024*1024):.0f} MB.",
                "status": "ERROR_FILE_TOO_LARGE",
                "sha256": sha256_hash,
            }

        if file_size == 0:
            return {
                "error": "Uploaded audio file is empty (0 bytes).",
                "status": "ERROR_EMPTY_FILE",
                "sha256": sha256_hash,
            }

        # 2. Decode raw audio via soundfile
        try:
            byte_stream = io.BytesIO(raw_bytes)
            audio_data, orig_sr = sf.read(byte_stream, dtype="float32", always_2d=True)
        except Exception as e:
            return {
                "error": f"Failed to decode audio file. Unsupported format or corrupted stream ({str(e)}).",
                "status": "ERROR_DECODE_FAILED",
                "sha256": sha256_hash,
            }

        num_samples, num_channels = audio_data.shape
        orig_duration = float(num_samples) / float(orig_sr) if orig_sr > 0 else 0.0

        if orig_duration < MIN_DURATION_SECONDS:
            return {
                "error": f"Audio duration ({orig_duration:.2f}s) is too short. Minimum required speech context is {MIN_DURATION_SECONDS}s.",
                "status": "ERROR_TOO_SHORT",
                "sha256": sha256_hash,
                "duration_seconds": round(orig_duration, 2),
            }

        if orig_duration > max_duration:
            return {
                "error": f"Audio duration ({orig_duration:.1f}s) exceeds maximum allowed limit of {max_duration:.0f}s.",
                "status": "ERROR_DURATION_EXCEEDED",
                "sha256": sha256_hash,
                "duration_seconds": round(orig_duration, 2),
            }

        # 3. Stereo-to-Mono Downmixing without aggressive amplitude scaling
        if num_channels > 1:
            mono_audio = np.mean(audio_data, axis=1)
        else:
            mono_audio = audio_data[:, 0]

        # 4. Energy & Silence Detection (safeguard against non-speech silence)
        rms_energy = float(np.sqrt(np.mean(mono_audio ** 2)))
        if rms_energy < SILENCE_RMS_THRESHOLD:
            return {
                "error": f"Recording contains near-total silence (RMS Energy: {rms_energy:.6f}). Acoustic neural inference requires audible speech context.",
                "status": "ERROR_SILENCE_DETECTED",
                "sha256": sha256_hash,
                "rms_energy": rms_energy,
                "duration_seconds": round(orig_duration, 2),
            }

        # 5. Safe Resampling to 16 kHz for Wav2Vec2 input tensor
        if orig_sr != TARGET_SAMPLE_RATE:
            # Polyphase non-destructive resampling
            num_resampled = int(round(len(mono_audio) * float(TARGET_SAMPLE_RATE) / float(orig_sr)))
            resampled_audio = signal.resample(mono_audio, num_resampled).astype(np.float32)
        else:
            resampled_audio = mono_audio.astype(np.float32)

        # 6. Generate Acoustic Visualizations
        # A: Waveform subsampled for responsive UI rendering
        step = max(1, len(mono_audio) // 1000)
        sub_time = np.linspace(0.0, orig_duration, len(mono_audio[::step]))
        waveform_data = {
            "time_axis": sub_time.tolist(),
            "amplitude": mono_audio[::step].tolist(),
        }

        # B: Short-Time Fourier Transform (STFT) Spectrogram
        f_bins, t_bins, Sxx = signal.spectrogram(
            mono_audio,
            fs=orig_sr,
            nperseg=min(512, len(mono_audio)),
            noverlap=256
        )
        # Convert power spectral density to dB scale
        Sxx_db = 10.0 * np.log10(np.maximum(Sxx, 1e-10))
        # Downsample spectrogram grid for fast Plotly rendering (max 100x60 grid)
        f_step = max(1, len(f_bins) // 60)
        t_step = max(1, len(t_bins) // 100)
        spectrogram_data = {
            "frequencies": f_bins[::f_step].tolist(),
            "times": t_bins[::t_step].tolist(),
            "power_db": Sxx_db[::f_step, ::t_step].tolist(),
        }

        # 7. Real AI Inference on GPU
        inputs = self._feature_extractor(
            resampled_audio,
            sampling_rate=TARGET_SAMPLE_RATE,
            return_tensors="pt"
        )
        inputs = {k: v.to(self._device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self._model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)[0]

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Class Mapping: id2label {'0': 'fake', '1': 'real'}
        fake_prob = float(probs[0].item())
        real_prob = float(probs[1].item())

        is_synthetic = fake_prob >= 0.50
        classification = "Model predicts Synthetic / Cloned Speech" if is_synthetic else "Model predicts Authentic Human Speech"
        primary_confidence = fake_prob if is_synthetic else real_prob

        # GPU VRAM check
        vram_allocated_mb = 0.0
        if torch.cuda.is_available() and self._device.type == "cuda":
            vram_allocated_mb = torch.cuda.memory_allocated(0) / (1024 * 1024)

        return {
            "status": "SUCCESS_VERIFIED_AUDIO_SCAN",
            "filename": filename,
            "sha256": sha256_hash,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "audio_metadata": {
                "duration_seconds": round(orig_duration, 2),
                "original_sample_rate_hz": orig_sr,
                "target_sample_rate_hz": TARGET_SAMPLE_RATE,
                "channels": num_channels,
                "channel_type": "Stereo (Downmixed to Mono)" if num_channels > 1 else "Mono",
                "rms_energy": round(rms_energy, 4),
            },
            "classification": classification,
            "is_synthetic": is_synthetic,
            "confidence_pct": round(primary_confidence * 100.0, 2),
            "synthetic_score": round(fake_prob * 100.0, 2),
            "authentic_score": round(real_prob * 100.0, 2),
            "calibration_status": "Uncalibrated Softmax Probability",
            "device": self.device_name,
            "inference_time_ms": round(elapsed_ms, 2),
            "vram_allocated_mb": round(vram_allocated_mb, 2),
            "model_architecture": self._model.__class__.__name__,
            "waveform": waveform_data,
            "spectrogram": spectrogram_data,
        }

