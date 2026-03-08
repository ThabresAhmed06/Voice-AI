import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import jiwer
import re

from services.stt_service import transcribe_audio
from services.semantic_service import extract_structured_data


TEST_FOLDER = "evaluation/test_audio"
GROUND_TRUTH_FILE = "evaluation/ground_truth.txt"


# ---------------- NUMBER NORMALIZATION ----------------

number_map = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9"
}


def normalize(text):

    text = text.lower()

    for word, num in number_map.items():
        text = re.sub(rf"\b{word}\b", num, text)

    text = re.sub(r"[^\w\s]", "", text)

    return text.strip()


# ---------------- AUDIO DURATION ----------------

def get_audio_duration(file_path):

    import wave

    with wave.open(file_path, "rb") as audio:

        frames = audio.getnframes()
        rate = audio.getframerate()

        duration = frames / float(rate)

    return duration


# ---------------- RTF ----------------

def compute_rtf(process_time, audio_length):

    return process_time / audio_length


# ---------------- MAIN EVALUATION ----------------

def main():

    with open(GROUND_TRUTH_FILE, "r") as f:

        rows = [line.strip().split("|") for line in f.readlines()]

    audio_files = sorted(os.listdir(TEST_FOLDER))

    total_wer = 0
    total_rtf = 0
    extraction_correct = 0

    print("\nEVALUATION TABLE\n")

    print(f"{'Test':<6}{'WER':<8}{'RTF':<8}{'Extraction':<12}")

    print("-" * 40)

    for i, audio_file in enumerate(audio_files):

        file_path = os.path.join(TEST_FOLDER, audio_file)

        reference = normalize(rows[i][0])

        expected_equipment = normalize(rows[i][1])
        expected_location = normalize(rows[i][2])
        expected_incident = normalize(rows[i][3])

        start = time.time()

        with open(file_path, "rb") as audio_stream:

            transcript = transcribe_audio(audio_stream)

        process_time = time.time() - start

        audio_length = get_audio_duration(file_path)

        rtf = compute_rtf(process_time, audio_length)

        transcript_norm = normalize(transcript)

        wer = jiwer.wer(reference, transcript_norm)

        structured = extract_structured_data(transcript)

        eq = normalize(structured.get("equipment", ""))
        loc = normalize(structured.get("location_or_unit", ""))
        inc = normalize(structured.get("incident_summary", ""))

        correct = (
            eq == expected_equipment and
            loc == expected_location and
            inc == expected_incident
        )

        if correct:
            extraction_correct += 1

        total_wer += wer
        total_rtf += rtf

        status = "✓" if correct else "✗"

        print(f"{i+1:<6}{wer:<8.3f}{rtf:<8.3f}{status:<12}")

    n = len(audio_files)

    avg_wer = total_wer / n
    avg_rtf = total_rtf / n
    extraction_acc = extraction_correct / n

    print("\nFINAL RESULTS\n")

    print("Average WER:", round(avg_wer, 3))
    print("Average RTF:", round(avg_rtf, 3))
    print("Extraction Accuracy:", round(extraction_acc * 100, 2), "%")


if __name__ == "__main__":
    main()