let mediaRecorder;
let audioChunks = [];
let stream;
let isRecording = false;

const recordBtn = document.getElementById("recordBtn");
const statusText = document.getElementById("status");
const transcriptBox = document.getElementById("transcriptBox");
const jsonBox = document.getElementById("jsonBox");

recordBtn.onclick = async () => {

    if (!isRecording) {

        try {

            stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });

            mediaRecorder = new MediaRecorder(stream);

            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {

                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {

                statusText.innerText = "⏳ Processing speech...";

                recordBtn.disabled = true;

                const blob = new Blob(audioChunks, { type: "audio/webm" });

                stream.getTracks().forEach(track => track.stop());

                const formData = new FormData();
                formData.append("audio", blob);

                try {

                    const response = await fetch("/upload_audio", {
                        method: "POST",
                        body: formData
                    });

                    const data = await response.json();

                    // Show transcript immediately
                    transcriptBox.innerText = data.transcript || "No transcript.";

                    if (data.needs_clarification) {

                        jsonBox.innerHTML = `
                        <div style="color:#facc15;font-weight:bold">
                        Clarification Needed
                        </div><br>
                        ${data.clarification_question}
                        `;

                        statusText.innerText = "Waiting for clarification";

                        recordBtn.disabled = false;

                        return;
                    }

                    const s = data.structured;

                    jsonBox.innerHTML = `
                    <b>Reporter:</b> ${s.reporter_name || "-"}<br><br>
                    <b>Department:</b> ${s.department || "-"}<br><br>
                    <b>Equipment:</b> ${s.equipment || "-"}<br><br>
                    <b>Location:</b> ${s.location_or_unit || "-"}<br><br>
                    <b>Date:</b> ${s.incident_date || "-"}<br><br>
                    <b>Time:</b> ${s.incident_time || "-"}<br><br>
                    <b>Incident:</b> ${s.incident_summary || "-"}<br><br>
                    <b>Severity:</b> ${s.severity || "-"}
                    `;

                    // Play confirmation audio
                    if (data.tts_audio_url) {

                        const audio = new Audio(data.tts_audio_url);

                        audio.play();
                    }

                    statusText.innerText = "Report recorded successfully";

                    recordBtn.disabled = false;

                } catch (error) {

                    console.error(error);

                    statusText.innerText = "Processing failed";

                    recordBtn.disabled = false;
                }
            };

            mediaRecorder.start();

            recordBtn.innerText = "Stop Recording";

            recordBtn.classList.add("recording");

            statusText.innerText = "Recording... Speak clearly";

            isRecording = true;

        } catch (error) {

            console.error(error);

            statusText.innerText = "Microphone access denied";
        }

    } else {

        mediaRecorder.stop();

        recordBtn.innerText = "Start Recording";

        recordBtn.classList.remove("recording");

        isRecording = false;
    }
};