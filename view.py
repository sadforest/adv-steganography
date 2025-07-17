import tkinter
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
import cv2
import controller

window = tk.Tk()
window.title('Image Steganography in the Frequency Domain')
window.geometry("1000x850")
window.maxsize(width=1000, height=1000)

def display_UI():
    window.mainloop()

def get_path():
    global path
    path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png")])
    return path

def update_psnr(psnr):
    psnr = "PSNR (db): " + str(psnr)
    psnr_label.config(text=psnr)

def update_mse(mse):
    mse = "MSE: " + str(mse)
    mse_label.config(text=mse)

def update_mer(mer):
    mer = "Maximum embedding range (bits): " + str(mer)
    mer_label.config(text=mer)

def update_filtered(filtered):
    filter_text = "Count of coefficients removed by filter: " + str(filtered)
    filtered_label.config(text=filter_text)

def upload_image(image_label):
    path = get_path()
    if path:
        img = Image.open(path)
        max_width = 600
        max_length = 600
        img.thumbnail((max_width, max_length))
        photo_image = ImageTk.PhotoImage(img)
        image_label.config(image=photo_image)
        image_label.image = photo_image
    return path

def show_embedded_image():
    embedded_image = cv2.imread('embedded_image.png')
    embedded_image = cv2.cvtColor(embedded_image, cv2.COLOR_BGR2RGB)
    tk_image = Image.fromarray(embedded_image)
    photo_image = ImageTk.PhotoImage(tk_image)
    embedded_image_label.config(image=photo_image)
    embedded_image_label.image = photo_image

check_var = tk.IntVar()
cmp_var = tk.IntVar()
gray = tk.IntVar()
cmp = tk.IntVar()
payload = "0"

def click_checkbox():
    if check_var.get():
        gray.set(1)
    else:
        gray.set(0)

def click_checkbox_cmp():
    if cmp_var.get():
        cmp.set(1)
    else:
        cmp.set(0)
def embed_request():
    gray_state = gray.get()
    payload = input.get()
    controller.view_request(path, gray_state, payload)

label = tk.Label(text="Image Steganography in the Frequency Domain", fg="black")
label.pack()

check = tk.Checkbutton(window, text="Calculate magnitude and phase?", variable=cmp, command=click_checkbox_cmp)
check.pack()

gray_check = tk.Checkbutton(window, text="Grayscale image?", variable=check_var, command=click_checkbox)
gray_check.pack()

input_label = tk.Label(text="Input custom payload below - 0 generates random large string")
input_label.pack()
input = tk.Entry(window, textvariable=payload)
input.insert(0, "0")
input.pack()

label = tk.Label(text="Upload image file for embedding (.jpg or .png)")
label.pack()
button = tk.Button(window, text='Open File', command=lambda: upload_image(cover_image_label))
button.pack()

embed_label = tk.Button(window, text="Embed image", command=lambda: embed_request())
embed_label.pack()

psnr_label = tk.Label(window, text="PSNR value: ")
mse_label = tk.Label(window, text="MSE value: ")
filtered_label = tk.Label(window, text="Count of coefficients removed by filter: ")
mer_label = tk.Label(window, text="Max embedding range (bits): ")
psnr_label.pack()
mse_label.pack()
filtered_label.pack()
mer_label.pack()

cover_image_label = tk.Label(window, width=500, height=500)
cover_image_label.pack(side=tkinter.LEFT)

embedded_image_label = tk.Label(window, width=500, height=500)
embedded_image_label.pack(side=tkinter.RIGHT)
