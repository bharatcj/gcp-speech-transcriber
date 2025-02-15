### GCP Speech-to-Text Transcriber

A Python script that transcribes call recordings stored in **Google Cloud Storage** using **Google Cloud Speech-to-Text API**.

## Features
- Fetches audio files from a **Google Cloud Storage Bucket**.
- Supports **speaker diarization** (detects multiple speakers).
- Uses **FFmpeg** to convert audio files to the required format.
- Deletes temporary files after transcription.

---

## **Installation**

### **1. Install Python and Required Libraries**
Ensure you have Python installed. If not, download and install it from [Python.org](https://www.python.org/downloads/).

Then, install the required dependencies:

```sh
pip3 install google-cloud-speech google-cloud-storage
```

Additionally, install **FFmpeg** (required for audio conversion):

#### **Windows**
1. Download **FFmpeg** from [FFmpeg official site](https://ffmpeg.org/download.html).
2. Extract it and add the `bin` folder to the system **PATH**.
3. Verify installation:
   ```sh
   ffmpeg -version
   ```

#### **Linux (Ubuntu)**
```sh
sudo apt update
sudo apt install ffmpeg
```

---

## **2. Configure Google Cloud API**
To use Google Cloud Speech-to-Text API, follow these steps:

1. **Go to Google Cloud Console**: [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable APIs**:
   - Go to **APIs & Services > Enable APIs & Services**.
   - Search for and enable:
     - **Cloud Speech-to-Text API**
     - **Cloud Storage API**
3. **Create a Service Account**:
   - Go to **APIs & Services > Credentials**.
   - Click **Create Credentials > Service Account**.
   - Fill in the details and click **Done**.
4. **Generate a JSON Key File**:
   - Click on the created service account.
   - Go to **Keys** and click **Add Key > Create New Key**.
   - Select **JSON** and download the file.
   - Save it in the project folder as `service_account.json`.

---

## **3. Running the Script**
### **Step 1: Clone the Repository**
```sh
git clone https://github.com/bharatcj/gcp-speech-transcriber.git
cd gcp-speech-transcriber
```

### **Step 2: Set Up Google Credentials**
Set the environment variable for authentication:

#### **Windows (CMD)**
```sh
set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service_account.json"
```

#### **Mac/Linux**
```sh
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account.json"
```

### **Step 3: Run the Script**
```sh
python3 transcribe_script.py <bucket_name> <folder_path> <search_term>
```
Replace:
- `<bucket_name>`: Google Cloud Storage bucket name.
- `<folder_path>`: Folder inside the bucket.
- `<search_term>`: A string (e.g., phone number + timestamp) to find the file.

Example:
```sh
python3 transcribe_script.py my-audio-bucket recordings 1234567890_20240215
```

---

## **4. Error Handling**
If an error occurs:
- The script prints a **detailed error message**.
- It **retries** API requests when possible.
- It logs any **file processing errors**.

---

## **5. Customization**
- Modify `transcribe_script.py` to change the **language code** (default: `es-ES` for Spanish).
- Adjust **speaker diarization settings** (change `min_speaker_count` and `max_speaker_count`).

---

## **6. License**
This project is licensed under the **MIT License**.

---

## **7. Contributing**
Contributions are welcome! Feel free to fork this repository and submit pull requests.

---

### **Author**
Developed by **Bharat CJ**  
GitHub: https://github.com/bharatcj