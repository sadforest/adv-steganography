import string
import numpy as np
import cv2
import struct
import random

def prepare_image(path):
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    red, green, blue = cv2.split(image)

    return red, green, blue
    # splits an image into RGB components

def transform_image(component):
    transformed_img = np.fft.fft2(component)
    return transformed_img
    # applies basic 2D DFT to image component

def calculate_phase(transformed_img):
    file = "phase.png"
    phase = np.angle(transformed_img)
    adjusted_phase = ((phase + np.pi / (np.pi * 2)).astype(np.uint8))
    cv2.imwrite(file, adjusted_phase)
    # calculates the phase information of a transform and writes it to a file

def calculate_magnitude(transformed_img):
    file = "magnitude.png"
    magnitude = 20 * np.log(np.abs(transformed_img))
    adjusted_magnitude = (np.log(magnitude + 1) / np.log(np.max(magnitude)+ 1)* 255)
    cv2.imwrite(file, adjusted_magnitude)
    # calculates the magnitude information of a transform and writes it to a file

def frequency_filter(transform_index):
    frequencies = np.fft.fftfreq(len(transform_index.keys()))
    remove_freqs = []
    cutoff = -0.4
    # calculates the frequency range associated with the magnitudes, and defines cutoff value
    set_length = len(transform_index.keys())
    for i, key in enumerate(transform_index.keys()):
        if frequencies[i] < cutoff:
            remove_freqs.append(key)
    for i in remove_freqs:
        transform_index.pop(i)
    # examines each frequency by their associated magnitude, if below the cutoff then removed
    filtered_set_length = len(transform_index.keys())
    filtered_coefficients = set_length-filtered_set_length

    return transform_index, filtered_coefficients

def index_transform(transformed_img):
    transform_index = {}

    for x in transformed_img:
        for y in x:
            transform_index.update({y.real: 0})
    # iterates through transformed image and adds their magnitude component to the index dictionary
    return transform_index

def get_reals(transform_index):
    real_list = []

    for key, value in transform_index.items():
        real_list.append(key)
    # generates list of real values for embedding
    return real_list

def calculate_binary(real_list):
    binary_list = []

    for i in real_list:
        bytes = struct.pack('!d', i)
        binary = ''.join(format(bits, '08b')for bits in bytes)
        binary_list.append(binary)
    # converts every float value in the real_list to their binary representation
    return binary_list

def convert_payload(payload):
    if type(payload) == int:
        output_string = bin(payload)
        output_string.format('b')
        return output_string
    # if payload is an int, simply convert it to binary
    p = ' '.join(format(ord(i), 'b') for i in payload)
    output_string = ''.join([p[i] for i in range(len(p)) if (i + 1) % 8 != 0])
    # otherwise, convert each character in the payload string to binary
    # logic operator removes blank spaces between bytes
    return output_string

def generate_payload():
    max_range = 30000
    # max_range can be modified to increase/decrease the payload size
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(max_range))
    # generates a string of random ASCII characters of length max_range
    return result_str
def generate_new_binary(binary_list, payload):
    embed_bits = -1
    # embed_bits can be modified to place the payload in a different bit position
    for index, character in enumerate(payload):
        new_str = binary_list[index][:embed_bits] + character
        binary_list[index] = new_str
    # iterates through payload characters and places them into the LSB of the magnitude
    # components in binary form
    # need to generate new boolean for this

def embed(transformed_img, transform_index, binary_list, real_list):
    for index, binary in enumerate(binary_list):
        new_float, = struct.unpack('!d',int(binary,2).to_bytes(8,'big'))
        # iterates through the modified binary list, converting the binary values back to floats and
        original_float = real_list[index]
        transform_index.update({original_float: new_float})
        # storing them as values in the transform index, with their original unmodified value as their keys

    for x in range(transformed_img.shape[0]):
        for y in range(transformed_img.shape[1]):
            complex = transformed_img[x, y]
            if complex.real in transform_index.keys():
                magnitude = transform_index.get(complex.real)
                phase = complex.imag * 1j
                new_complex = np.complex128(magnitude+phase)
                transformed_img[x, y] = new_complex
    # traverses through the 2D transform array, for each element checking if its magnitude component is in
    # the transform index (not filtered). if so, replace transform array value with embedded value

def transform_component(image, payload):
    transform = transform_image(image)
    transform_index = index_transform(transform)
    transform_index, filtered_count = frequency_filter(transform_index)
    real_list = get_reals(transform_index)
    bin_list = calculate_binary(real_list)
    generate_new_binary(bin_list, payload)
    embed(transform, transform_index, bin_list, real_list)
    return transform, filtered_count
    # applies methods to transform and embed a component

def calculate_mse(cover_image, embedded_image):
    mse = np.mean((cover_image - embedded_image)**2)
    return mse
    # calculates mean squared error

def calculate_psnr(cover_image, embedded_image):
    embedded_image = np.uint8(embedded_image)
    cover_image = np.uint8(cover_image)
    # standardizes encoding scheme, needed to avoid errors
    mse = calculate_mse(cover_image, embedded_image)
    pixel_max = 255.0
    psnr_value = 20 * np.log10(pixel_max / np.sqrt(mse))
    return psnr_value
    # calculates peak signal to noise ratio

def max_embedding_range(transformed_img):
    mer = 0
    for x in range(transformed_img.shape[0]):
        for y in range(transformed_img.shape[1]):
            mer += 1
    return mer
    # calculates max embedding range, +1 value in array = +1 bit

def embed_image(path, gray, payload):
    if payload == "0":
        payload = convert_payload(generate_payload())
    else:
        payload = convert_payload(payload)
    # converts payload to binary, if no payload input then generate payload
    if(gray == 1):
        # if grayscale image
        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        embedded_image, filtered_count = transform_component(image, payload)
        reconstructed_image = np.fft.ifft2(embedded_image).real
        # read image, embed image with payload and reconstruct
        calculate_phase(embedded_image)
        calculate_magnitude(embedded_image)

        mse = calculate_mse(image, reconstructed_image)
        psnr = calculate_psnr(image, reconstructed_image)
        max_embed_range = max_embedding_range(reconstructed_image)

        # calculate various metrics
        file = 'embedded_image.png'
        cv2.imwrite(file, reconstructed_image)

        return reconstructed_image, psnr, mse, max_embed_range, filtered_count
    else:
        # if colour image
        image = cv2.imread(path)
        metric_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        tranf_image = transform_image(metric_image)
        calculate_phase(tranf_image)
        calculate_magnitude(tranf_image)

        red, green, blue = prepare_image(path)

        separate = (len(payload)//3)
        red_payload = payload[:separate]
        green_payload = payload[separate:2 * separate]
        blue_payload = payload[2 * separate:]
        # separate image into components and split payload into 3
        transform_red, filtered_red = transform_component(red, red_payload)
        transform_green, filtered_green = transform_component(green, green_payload)
        transform_blue, filtered_blue = transform_component(blue, blue_payload)
        filtered_count = filtered_red + filtered_green + filtered_blue
        # embed 3 image components with their respective payload.
        # tracks filtered frequency amount across components

        r = np.fft.ifft2(transform_red).real
        g = np.fft.ifft2(transform_green).real
        b = np.fft.ifft2(transform_blue).real
        # inverse transform for 3 embedded components

        embedded_image = cv2.merge([r, g, b])
        reconstructed_image = np.float32(embedded_image)
        # reconstructed_image = cv2.cvtColor(reconstructed_image, cv2.COLOR_BGR2RGB)
        # reconstructs image and normalises

        file = 'embedded_image.png'
        cv2.imwrite(file, reconstructed_image)

        metric_reconstruct = cv2.cvtColor(reconstructed_image, cv2.COLOR_BGR2GRAY)
        mse = calculate_mse(metric_image, metric_reconstruct)
        psnr = calculate_psnr(metric_image, metric_reconstruct)
        max_embed_range = max_embedding_range(metric_reconstruct)

        return reconstructed_image, psnr, mse, max_embed_range, filtered_count

def extract(embedded_image, payload):
    message = ""
    transform = transform_image(embedded_image)
    transform_index = index_transform(transform)
    index = 0
    length = len(payload)

    for i in transform_index.keys():
        if index < length:
            bytes = struct.pack('!d', i)
            binary = ''.join(format(bits, '08b') for bits in bytes)
            payload_char = binary[-1]
            message = message + payload_char
        index+=1
    return message
    # reconstructs payload
