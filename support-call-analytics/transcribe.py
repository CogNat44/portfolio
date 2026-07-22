import whisper
import torchaudio
import os
import sys
import re
import warnings
import torch
import tempfile

warnings.filterwarnings("ignore")

# PyTorch 2.6+ defaults weights_only=True which breaks pyannote model loading.
# Force weights_only=False for trusted pyannote/speechbrain model files.
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

from pyannote.audio import Pipeline

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTED_DIR = os.path.join(BASE_DIR, "audio")        # input MP3 files
OUTPUT_DIR = os.path.join(BASE_DIR, "transcripts")     # output transcript .txt files
HF_TOKEN = os.environ.get("HF_TOKEN")  # set via: export HF_TOKEN=your_token_here


def parse_filename(filename):
    """Extract phone number, date, and time from filename."""
    match = re.match(
        r"Call recording of (\(\d{3}\) \d{3}-\d{4}) at (\d{4}-\d{2}-\d{2}) (\d{2}-\d{2}-\d{2})\.mp3",
        filename,
    )
    if match:
        phone = match.group(1)
        date = match.group(2)
        time_raw = match.group(3).replace("-", ":")
        return phone, date, time_raw
    return "Unknown", "Unknown", "Unknown"


def assign_speakers_to_segments(diarization, whisper_segments):
    """Map pyannote speaker labels onto whisper transcript segments."""
    for seg in whisper_segments:
        mid = (seg["start"] + seg["end"]) / 2
        speaker = "Unknown"
        for turn, _, spk in diarization.itertracks(yield_label=True):
            if turn.start <= mid <= turn.end:
                speaker = spk
                break
        seg["speaker"] = speaker
    return whisper_segments


def transcribe_file(whisper_model, diarize_pipeline, filepath):
    """Transcribe and diarize a single MP3 file."""
    filename = os.path.basename(filepath)
    phone, date, time = parse_filename(filename)

    print(f"  Transcribing with Whisper...")
    result = whisper_model.transcribe(filepath, language="en", verbose=False)

    segments = [
        {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
        for s in result["segments"]
    ]

    print(f"  Diarizing with pyannote ({len(segments)} segments)...")
    # Convert to 16kHz mono WAV for pyannote compatibility (avoids tensor size mismatches)
    waveform, sr = torchaudio.load(filepath)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if sr != 16000:
        waveform = torchaudio.functional.resample(waveform, sr, 16000)
    # Pad to nearest 10-second boundary to avoid pyannote chunking issues
    target_len = ((waveform.shape[1] // 160000) + 1) * 160000
    if waveform.shape[1] < target_len:
        waveform = torch.nn.functional.pad(waveform, (0, target_len - waveform.shape[1]))
    tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    torchaudio.save(tmp_wav.name, waveform, 16000)
    tmp_wav.close()
    diarization = diarize_pipeline(tmp_wav.name, num_speakers=2)
    os.unlink(tmp_wav.name)

    segments = assign_speakers_to_segments(diarization, segments)

    # Force exactly 2 speakers: keep the two most frequent, merge any others
    from collections import Counter
    spk_counts = Counter(seg["speaker"] for seg in segments)
    top_two = [spk for spk, _ in spk_counts.most_common(2)]

    if len(spk_counts) > 2:
        # For each minor speaker, merge into whichever top speaker spoke closest in time
        for seg in segments:
            if seg["speaker"] not in top_two:
                # Find nearest top-speaker segment by time
                best = top_two[0]
                best_dist = float("inf")
                for other in segments:
                    if other["speaker"] in top_two:
                        dist = abs(seg["start"] - other["start"])
                        if dist < best_dist:
                            best_dist = dist
                            best = other["speaker"]
                seg["speaker"] = best

    # Assign consistent numbering based on who speaks first
    unique_speakers = []
    for seg in segments:
        if seg["speaker"] not in unique_speakers:
            unique_speakers.append(seg["speaker"])
    speaker_map = {spk: f"Speaker {i+1}" for i, spk in enumerate(unique_speakers)}

    # Build transcript with speaker labels, merging consecutive same-speaker segments
    transcript_lines = []
    current_speaker = None
    current_text = []

    for seg in segments:
        label = speaker_map.get(seg["speaker"], seg["speaker"])
        if label != current_speaker:
            if current_speaker is not None:
                transcript_lines.append(
                    f"[{current_speaker}]: {' '.join(current_text)}"
                )
            current_speaker = label
            current_text = [seg["text"]]
        else:
            current_text.append(seg["text"])

    if current_speaker and current_text:
        transcript_lines.append(f"[{current_speaker}]: {' '.join(current_text)}")

    transcript_body = "\n\n".join(transcript_lines)

    output = f"""File Name: {filename}
Call Date: {date}
Call Time: {time}
Phone Number: {phone}

--- Transcript ---

{transcript_body}
"""
    return output


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    files = sorted(
        [f for f in os.listdir(EXTRACTED_DIR) if f.endswith(".mp3")]
    )

    if offset:
        files = files[offset:]
    if limit:
        files = files[:limit]

    print("Loading Whisper medium model...")
    whisper_model = whisper.load_model("medium")

    print("Loading pyannote diarization pipeline...")
    diarize_pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=HF_TOKEN,
    )

    # Note: pyannote has known issues on MPS, so we keep it on CPU
    print("Running diarization on CPU (MPS not stable for pyannote)")

    print(f"\nProcessing {len(files)} files...\n")

    for i, filename in enumerate(files, 1):
        filepath = os.path.join(EXTRACTED_DIR, filename)
        print(f"[{i}/{len(files)}] {filename}")

        try:
            output = transcribe_file(whisper_model, diarize_pipeline, filepath)

            out_name = os.path.splitext(filename)[0] + ".txt"
            out_path = os.path.join(OUTPUT_DIR, out_name)
            with open(out_path, "w") as f:
                f.write(output)

            print(f"  Saved: {out_name}\n")
        except Exception as e:
            print(f"  ERROR: {e}\n")

    print("Done!")


if __name__ == "__main__":
    main()
