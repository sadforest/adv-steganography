import view
import model
import cv2

def view_request(path, gray, payload):
    embedded_image, psnr, mse, mer, filtered_count = model.embed_image(path, gray, payload)
    model_request(embedded_image, psnr, mse, mer, filtered_count)
    # handles view request

def model_request(embedded_image, psnr, mse, mer, filtered_count):
    view.show_embedded_image()
    view.update_psnr(psnr)
    view.update_mse(mse)
    view.update_mer(mer)
    view.update_filtered(filtered_count)

if __name__ == "__main__":
    view.display_UI()
    # runs UI
