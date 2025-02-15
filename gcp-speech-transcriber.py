import os
import sys
import json
import subprocess
from google.cloud import speech, storage
from google.cloud.speech import RecognitionConfig, RecognitionAudio

# Set Google Cloud credentials (Replace with your actual JSON key file path)
current_path = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_path, "your_google_cloud_credentials.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_path

def list_blobs_with_prefix(bucket_name, prefix, delimiter=None):
    """List all files in a GCS bucket with a given prefix."""
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter)
    return blobs

def search_file(bucket_name, folder_path, search_term):
    """Search for a specific file in a GCS bucket based on search term."""
    search_parts = search_term.split('_')
    if len(search_parts) < 2:
        return []
    
    phone_number, timestamp = search_parts[0], search_parts[1]

    blobs = list_blobs_with_prefix(bucket_name, prefix=folder_path)
    matching_blobs = [
        blob.name for blob in blobs 
        if phone_number in blob.name and timestamp in blob.name
    ]
    return matching_blobs

def convert_audio_format(input_file_path, output_file_path):
    """Convert audio file to mono channel and 16kHz sample rate using FFmpeg."""
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_file_path, "-ac", "1", "-ar", "16000", output_file_path],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return {"status": "success", "message": f"Converted {input_file_path} to {output_file_path}"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Error converting audio format: {e}"}

def transcribe_audio(gcs_uri, language_code="es-ES"):
    """Transcribe an audio file stored in GCS using Google Cloud Speech-to-Text API."""
    client = speech.SpeechClient()
    audio = RecognitionAudio(uri=gcs_uri)
    
    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=10,
    )
    config = RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000, 
        language_code=language_code,
        diarization_config=diarization_config,
        use_enhanced=True,
        model="phone_call",
    )

    try:
        operation = client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=10000)
        transcript = "\n".join([result.alternatives[0].transcript for result in response.results])
        return {"status": "success", "transcript": transcript}
    except Exception as e:
        return {"status": "error", "message": f"Error during transcription: {e}"}

def delete_blob(bucket_name, blob_name):
    """Delete a file from a GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

def main():
    """Main script execution for transcribing a file from GCS."""
    if len(sys.argv) != 4:
        print(json.dumps({"status": "error", "message": "Usage: python3 transcribe_script.py <bucket_name> <folder_path> <search_term>"}))
        return

    bucket_name = sys.argv[1]
    folder_path = sys.argv[2]
    search_term = sys.argv[3]
    temp_dir = "/tmp"

    matching_files = search_file(bucket_name, folder_path, search_term)
    if not matching_files:
        print(json.dumps({"status": "error", "message": f"No call recordings matching in the Google Cloud Storage Bucket with the given {search_term}"}))
        return

    file_path = matching_files[0]
    gcs_uri = f"gs://{bucket_name}/{file_path}"
    local_file_path = os.path.join(temp_dir, file_path.split('/')[-1])
    converted_file_path = os.path.join(temp_dir, f"converted_{file_path.split('/')[-1]}")

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        blob.download_to_filename(local_file_path)

        conversion_result = convert_audio_format(local_file_path, converted_file_path)
        if conversion_result["status"] == "error":
            print(json.dumps(conversion_result))
            return

        new_blob_name = f"{folder_path}/converted_{os.path.basename(file_path)}"
        new_blob = bucket.blob(new_blob_name)
        new_blob.upload_from_filename(converted_file_path, timeout=10000)
        gcs_uri_converted = f"gs://{bucket_name}/{new_blob_name}"

        # Transcribe the audio
        transcription_result = transcribe_audio(gcs_uri_converted)
        if transcription_result["status"] == "error":
            print(json.dumps(transcription_result))
            return

        transcript = transcription_result["transcript"]

        delete_blob(bucket_name, new_blob_name)

        os.remove(local_file_path)
        os.remove(converted_file_path)

        print(json.dumps({"status": "success", "transcript": transcript}))

    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Error processing file {file_path}: {e}"}))

if __name__ == '__main__':
    main()