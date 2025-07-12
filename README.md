# 🕵️‍♂️ LSB Steganography Tool (Python + Tkinter GUI)

This project allows you to hide (encode) and extract (decode) files or text inside images using **Least Significant Bit (LSB) Steganography**. It features a clean **Tkinter-based GUI** for ease of use.

---

## 📌 Features

- 🔐 Hide any file (text, images, documents) inside an image
- 💬 Hide plain text with one click
- 🖼️ Simple image preview inside GUI
- 🧠 Detect if an image contains hidden data
- ✅ Supports `.png`, `.bmp`, and `.jpg` formats (lossless preferred)

---

## 🧠 How LSB Works

LSB steganography hides data by modifying the **least significant bits** of pixel values. Changes are so subtle that the image looks visually unchanged, while your secret data remains hidden inside.

---

## 🖥️ GUI Preview

![image](https://github.com/user-attachments/assets/5562e236-8362-4a69-b5c4-75d1ac2bf67d)

---

## 🛠️ Technologies Used

- `Python 3`
- `Tkinter` – GUI library
- `OpenCV` – Image processing
- `NumPy` – Array operations
- `Pillow` – Image preview

---

## 🚀 How to Run

1. Clone this repo:
   ```bash
   git clone https://github.com/yourusername/lsb-steganography-tool.git
   cd lsb-steganography-tool
    ````

2. Install dependencies:

   ```bash
   pip install pillow opencv-python numpy
   ```

3. Run the app:

   ```bash
   python main.py
   ```

---

## 🧪 Features in Detail

| Function               | Description                                                   |
| ---------------------- | ------------------------------------------------------------- |
| 📤 Select Image        | Choose the image to use as a carrier                          |
| 📁 Select File to Hide | Pick any file (PDF, DOCX, ZIP, etc.) to hide inside the image |
| 📝 Encode Text         | Type a secret message to be embedded as a `.txt` file         |
| 🔍 Detect Hidden Data  | Check if the image contains any stego content                 |
| 📥 Decode              | Extract hidden data back to its original file                 |

---

## ⚠️ Limitations

* Use lossless formats like `.png` or `.bmp`. JPEG is not reliable.
* Large files require high-resolution carrier images.
* Basic LSB steganography – not encrypted or secure against deep steganalysis.

---

## 🧑‍💻 Author

**Darsani**
Cybersecurity Enthusiast    
