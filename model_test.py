import unittest
import model
import cv2
import numpy as np
import os
import time

def test_transform(image):
    transform = model.transform_image(image)
    assert isinstance(transform, np.ndarray)
    # asserts that images are correctly transformed into numpy 2d arrays

def test_magnitude_calculation(image):
    file = 'magnitude.png'
    transform = model.transform_image(image)
    model.calculate_magnitude(transform)
    assert os.path.exists(file)

def test_phase_calculation(image):
    file = 'phase.png'
    transform = model.transform_image(image)
    model.calculate_phase(transform)
    assert os.path.exists(file)
    # asserts that the phase image is produced

def test_frequency_filter(image):
    transform = model.transform_image(image)
    transform_index = model.index_transform(transform)
    index_length = len(transform_index.keys())

    transform_index, filtered = model.frequency_filter(transform_index)
    filtered_index_length = len(transform_index.keys())

    maximum_difference = index_length * 0.12
    assert(abs(index_length - filtered_index_length) <= maximum_difference)
    # asserts that the frequency filter is removing no more than 12% of the low frequency areas from the image

def test_runtime(image):
    start = time.time()
    transform = model.embed_image('kinsale.png', 1, "0")
    end = time.time()
    run_time = end - start

def test_max_embedding_range(image):
    max_length = 600000
    min_length = 450000
    # estimated by external library for comparison

    assert(model.max_embedding_range(image) >= 450000)
    assert(model.max_embedding_range(image) <= 600000)

def test_mse(image):
    mse = model.calculate_mse(image, image)
    assert(mse == 0)
    #same image, should be 0

def test_convert_payload():
    int_payload = model.convert_payload(3)
    assert (int_payload == '0b11')
    #testing that int payloads are converted

def test_payload_generation():
    string = model.generate_payload()
    assert(len(string) == 20000)

def test_binary_generation():
    payload = model.convert_payload("a")

    bin_list = []
    bin_list.append("10110110")
    bin_list.append("10110110")
    bin_list.append("10110110")
    bin_list.append("10110110")
    bin_list.append("10110110")
    bin_list.append("10110110")
    bin_list.append("10110110")
    bin_list = model.generate_new_binary(bin_list, payload)
    lsb = bin_list[0]
    lsb = bin_list[:-1]
    assert(lsb == "1")

def test_transform_component(image):
    transform = model.transform_image(image)
    assert(type(transform) == np.ndarray)

def test_image_separation():
    returned = model.prepare_image("kinsale.png")
    assert(len(returned) == 3)
    # should return 3 components for R,G,B

if __name__ == '__main__':
    # reads in test image and runs tests
    image = cv2.imread("kinsale.png")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    test_transform(image)
    test_magnitude_calculation(image)
    test_phase_calculation(image)
    test_frequency_filter(image)
    test_runtime(image)
    test_max_embedding_range(image)
    test_mse(image)
    test_convert_payload()
    test_payload_generation()
    test_transform_component(image)
    test_image_separation()
    print("All tests passed")
