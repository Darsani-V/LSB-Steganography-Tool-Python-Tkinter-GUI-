import tkinter as tk
from tkinter import filedialog, messagebox, Label, Entry
from PIL import Image, ImageTk
import cv2
import numpy as np
import os


class SteganographyException(Exception):
    pass


class LSBSteg():
    def __init__(self, im):
        self.image = im
        self.height, self.width, self.nbchannels = im.shape
        self.size = self.width * self.height

        self.maskONEValues = [1, 2, 4, 8, 16, 32, 64, 128]
        self.maskONE = self.maskONEValues.pop(0)

        self.maskZEROValues = [254, 253, 251, 247, 239, 223, 191, 127]
        self.maskZERO = self.maskZEROValues.pop(0)

        self.curwidth = 0
        self.curheight = 0
        self.curchan = 0

    def put_binary_value(self, bits):
        for c in bits:
            val = list(self.image[self.curheight, self.curwidth])
            if int(c) == 1:
                val[self.curchan] |= self.maskONE
            else:
                val[self.curchan] &= self.maskZERO

            self.image[self.curheight, self.curwidth] = tuple(val)
            self.next_slot()

    def next_slot(self):
        if self.curchan == self.nbchannels - 1:
            self.curchan = 0
            if self.curwidth == self.width - 1:
                self.curwidth = 0
                if self.curheight == self.height - 1:
                    self.curheight = 0
                    if self.maskONE == 128:
                        raise SteganographyException("No available slot remaining (image filled)")
                    else:
                        self.maskONE = self.maskONEValues.pop(0)
                        self.maskZERO = self.maskZEROValues.pop(0)
                else:
                    self.curheight += 1
            else:
                self.curwidth += 1
        else:
            self.curchan += 1

    def read_bit(self):
        val = self.image[self.curheight, self.curwidth][self.curchan]
        val = val & self.maskONE
        self.next_slot()
        return "1" if val > 0 else "0"

    def read_byte(self):
        return self.read_bits(8)

    def read_bits(self, nb):
        return "".join(self.read_bit() for _ in range(nb))

    def byteValue(self, val):
        return self.binary_value(val, 8)

    def binary_value(self, val, bitsize):
        binval = bin(val)[2:]
        return binval.zfill(bitsize)

    def encode_binary(self, data, extension=None):
        ext = extension.encode() if extension else b""
        ext_len = len(ext)
        signature = b"LSBv1"  # 5 bytes signature
        data = signature + len(ext).to_bytes(2, 'big') + ext + data
        l = len(data)
        if self.width * self.height * self.nbchannels < l + 64:
            raise SteganographyException("Carrier image not big enough to hold all the data")
        self.put_binary_value(self.binary_value(l, 64))
        for byte in data:
            self.put_binary_value(self.byteValue(byte))
        return self.image

    def decode_binary(self):
        l = int(self.read_bits(64), 2)
        data = bytearray()
        for _ in range(l):
            data.append(int(self.read_byte(), 2))

        if data[:5] != b"LSBv1":
            raise SteganographyException("No valid hidden data found")

        ext_len = int.from_bytes(data[5:7], 'big')
        ext = data[7:7 + ext_len].decode()
        payload = data[7 + ext_len:]
        return payload, ext

    def has_hidden_data(self):
        try:
            saved_pos = (self.curwidth, self.curheight, self.curchan, self.maskONE, self.maskZERO,
                         list(self.maskONEValues), list(self.maskZEROValues))
            l = int(self.read_bits(64), 2)
            bytes_ = bytearray()
            for _ in range(min(l, 5)):
                bytes_.append(int(self.read_byte(), 2))
            self.curwidth, self.curheight, self.curchan, self.maskONE, self.maskZERO, self.maskONEValues, self.maskZEROValues = saved_pos
            return bytes_[:5] == b"LSBv1"
        except:
            return False


class LSBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LSB Steganography")
        self.root.geometry("620x600")
        self.root.configure(bg="#1e1e1e")

        self.input_path = ""
        self.file_to_hide = ""

        style = {
            "font": ("Segoe UI", 10),
            "bg": "#2e2e2e",
            "fg": "white",
            "activebackground": "#3e3e3e",
            "activeforeground": "white",
            "relief": tk.FLAT,
            "bd": 1,
            "highlightthickness": 0,
            "padx": 10,
            "pady": 5
        }

        self.image_label = Label(root, text="Selected Image: None", bg="#1e1e1e", fg="white", font=("Segoe UI", 10))
        self.image_label.pack(pady=5)

        self.image_canvas = tk.Canvas(root, width=300, height=200, bg='#2e2e2e', highlightthickness=1, highlightbackground="#444")
        self.image_canvas.pack(pady=5)

        tk.Button(root, text="Select Image", command=self.select_image, **style).pack(pady=5)
        tk.Button(root, text="Select File to Hide", command=self.select_file, **style).pack(pady=5)

        tk.Label(root, text="Text to Encode:", bg="#1e1e1e", fg="white", font=("Segoe UI", 10)).pack(pady=5)
        self.text_entry = Entry(root, width=60, bg="#2e2e2e", fg="white", insertbackground="white", font=("Segoe UI", 10))
        self.text_entry.pack(pady=5)

        tk.Button(root, text="Encode File", command=self.encode_file, **style).pack(pady=5)
        tk.Button(root, text="Encode Text", command=self.encode_text, **style).pack(pady=5)
        tk.Button(root, text="Decode", command=self.decode, **style).pack(pady=5)
        tk.Button(root, text="Detect Hidden Data", command=self.detect_hidden_data, **style).pack(pady=10)

    def select_image(self):
        self.input_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.bmp *.jpg")])
        if self.input_path:
            self.image_label.config(text=f"Selected Image: {os.path.basename(self.input_path)}")
            img = Image.open(self.input_path)
            img.thumbnail((300, 200))
            self.tk_img = ImageTk.PhotoImage(img)
            self.image_canvas.create_image(150, 100, image=self.tk_img)

    def select_file(self):
        self.file_to_hide = filedialog.askopenfilename()

    def encode_file(self):
        if not self.input_path or not self.file_to_hide:
            messagebox.showerror("Error", "Select both image and file")
            return
        image = cv2.imread(self.input_path)
        steg = LSBSteg(image)
        data = open(self.file_to_hide, "rb").read()
        ext = os.path.splitext(self.file_to_hide)[1]
        try:
            res = steg.encode_binary(data, ext)
            output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if output_path:
                cv2.imwrite(output_path, res)
                messagebox.showinfo("Success", "File hidden successfully")
        except SteganographyException as e:
            messagebox.showerror("Error", str(e))

    def encode_text(self):
        if not self.input_path or not self.text_entry.get():
            messagebox.showerror("Error", "Select image and enter text")
            return
        image = cv2.imread(self.input_path)
        steg = LSBSteg(image)
        data = self.text_entry.get().encode()
        try:
            res = steg.encode_binary(data, ".txt")
            output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if output_path:
                cv2.imwrite(output_path, res)
                messagebox.showinfo("Success", "Text hidden successfully")
        except SteganographyException as e:
            messagebox.showerror("Error", str(e))

    def decode(self):
        if not self.input_path:
            messagebox.showerror("Error", "Select an image first")
            return
        image = cv2.imread(self.input_path)
        steg = LSBSteg(image)
        try:
            data, ext = steg.decode_binary()
            output_path = filedialog.asksaveasfilename(defaultextension=ext)
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(data)
                messagebox.showinfo("Success", "File extracted successfully")
        except SteganographyException as e:
            messagebox.showerror("Error", str(e))

    def detect_hidden_data(self):
        if not self.input_path:
            messagebox.showerror("Error", "Select an image first")
            return
        image = cv2.imread(self.input_path)
        steg = LSBSteg(image)
        if steg.has_hidden_data():
            messagebox.showinfo("Detection", "Hidden data detected in image.")
        else:
            messagebox.showinfo("Detection", "No hidden data found in image.")


if __name__ == '__main__':
    root = tk.Tk()
    app = LSBApp(root)
    root.mainloop()
