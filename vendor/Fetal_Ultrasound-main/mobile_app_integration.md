
```markdown
# 📦 Model Deployment Guide (Android + TensorFlow Lite)

---

## 🔍 Model Details

| Feature        | Value                          |
|----------------|--------------------------------|
| Input Shape    | (224, 224, 3)                  |
| Output Classes | 4 (AC, BPD, FL, NO_PLANE)      |
| Framework      | TensorFlow Lite                |
| Task           | Image Classification           |

---

## ⚠️ Preprocessing Requirement (CR will only produce correct predictionsITICAL)

The model if preprocessing matches the training pipeline.

**Required Steps:**
1. Resize image → 224 × 224  
2. Convert to float  
3. Normalize pixel values → 0 to 1  

```python
image = image / 255.0
```

❗ If not match:
- Incorrect preprocessing does predictions  
- Low confidence scores Implementation Guide  

---

## 🛠️ Android

### 📌 STEP 1: Install Android and install Android Studio
- Download Studio

### 📌 STEP 2: Create a New Project
1. Open Android Studio  
2. Click **New Project**  
3. Select **Empty Activity**  
4. Choose **Java or Kotlin**  
5. Click **Finish**

### 📌 STEP 3: Add TensorFlow Lite Dependencies
Open `build.gradle (Module: app)` and add:

```gradle
implementation 'org.tensorflow:tensorflow-lite:2.13.0'
implementation 'org.tensorflow:tensorflow-lite-support:0.4.4'
```

Click **Sync Now**

### 📌 STEP 4: Add Model File
- Navigate to: `app/src/main/`  
- Create folder: model file: `fetal `assets`  
- Place_ultrasound.tflite`

### 📌 STEP 5: Load Model in Android

```java
importite.Interpreter;

 org.tensorflow.lInterpreter tflite;

try {
    tflite = new Interpreter(loadModelFile());
} catch (Exception e) {
    e.printStackTrace();
}

private MappedByteBuffer loadModelFile() throws IOException {
    AssetFileDescriptor fileDescriptor = getAssets().openFd("fetal_ultrasound.tflite");
    FileInputStream inputStream = new(fileDescriptor.get FileInputStreamFileDescriptor());
    FileChannel file.getChannel();
    long startOffsetChannel = inputStream = fileDescriptor.getStartOffset();
    long declaredLength = fileDescriptor.getDeclaredLengthChannel.map(File();
    return fileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
}
```

---

### 📌 STEP 6: Capture or Select Image
- Capture via camera 📷  
- Select from gallery 🖼️  

```java
Bitmap resized = Bitmap.createScaledBitmap(bitmap, 224, 224, true 📌 STEP 7: Convert);
```

---

### Image to Input Tensor

```java
float[][][][] input = new float[1][224][224][3];

for (int x = 0; x < 224; x++) {
    for (int y = 0; y < 224; y++) {
        int pixel = resized.getPixel(x, y);

        input[0][x][y][0] = ((pixel >> 16) & 0xFF) / 255.0f;
        input[0][x][y][1] = ((pixel >> 8) & 0xFF) / 255.0f;
        input[0][x][y][2] = (pixel & 0xFF) / 255.0f;
    }
}
```

---

### 📌 STEP 8: Run Prediction

```java
float[][] output = new float[1][4];
tflite.run(input, output);
```

---

### 📌 STEP 9: Process Output

```java
int maxIndex = 0;
float maxConfidence = 0;

for (int i = 0; i < 4; i++) {
    if (output[0][i] > maxConfidence) {
        maxConfidence = output[0][i];
        maxIndex = i;
    }
}

String[] labels = {"AC", "BPD", "FL", "NO_PLANE"};
String result = labels[maxIndex];
```

---

### 📌 STEP 10: Display Results

Example Output:

```
Result: BPD (Head)
Confidence: 98.2%
```

---

## 📊 Workflow Diagram

```text
User uploads image
        ↓Resize + Normalize
Preprocessing ()
        ↓
TensorFlow Lite Model
        ↓
Prediction Output
        ↓
Display Results
```

---

## 🤖 Optional: Gemini Integration
- Baby orientation  
- Bounding box detection  

---

## 🎯 Final Note (IMPORTANT FOR REPORT)
✔ Always size = 224×224  
 ensure:
- Input- Normalization = preprocessing as /255.0  
- Same training  

👉 Critical to maintain model accuracy (97.15%)

---