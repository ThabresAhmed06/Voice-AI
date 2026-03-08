import sounddevice as sd
import soundfile as sf
import os

# Folder where audio will be saved
OUTPUT_FOLDER = "test_audio"

# Recording settings
SAMPLE_RATE = 16000
CHANNELS = 1

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def record_audio(filename):

    duration = int(input("Enter recording duration (seconds): "))

    print("Recording... Speak now")

    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS
    )

    sd.wait()

    filepath = os.path.join(OUTPUT_FOLDER, filename)

    sf.write(filepath, audio, SAMPLE_RATE)

    print(f"Saved: {filepath}\n")


def main():

    print("Audio Recording Tool for Evaluation\n")

    index = 1

    while True:

        filename = f"test{index}.wav"

        record_audio(filename)

        cont = input("Record another? (y/n): ")

        if cont.lower() != "y":
            break

        index += 1


if __name__ == "__main__":
    main()