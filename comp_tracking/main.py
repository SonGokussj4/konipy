"""Main script file - Simple script"""

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from dataloader import load_images_from_dir, load_xml_from_dir, DataFrame

import cv2

# ENVIROMENT VARIABLES
load_dotenv()

DEBUG = os.getenv("DEBUG")
if DEBUG == "True":
    API_BASE_URL = "http://localhost:8989"
else:
    API_BASE_URL = os.getenv("API_BASE_URL", "")

# CONSTANTS
CURDIR = Path(__file__).parent
# Color pallete - BGR format (OpenCV)
COLOR_PALLETE = {
    0: (0, 0, 255),
    1: (0, 255, 0),
    2: (0, 255, 255),
    3: (255, 0, 255),
    4: (255, 255, 0),
    5: (255, 0, 0),
}


def main():
    """Main function."""
    print("Hello world!")

    shop_path = CURDIR / "shop"
    print("shop_path:", shop_path)

    imgs = load_images_from_dir((shop_path / "*.jpg").as_posix())
    # print(imgs)
    xmls = load_xml_from_dir((shop_path / "*.xml").as_posix())
    print(f"[ DEBUG ] xmls: {xmls}")

    # Assign random IDs to the bounding boxes in first xml
    first_picture = DataFrame(xmls[0], shop_path)
    first_picture.assign_ids()
    print(f"[ DEBUG ] first: {first_picture}")

    # Send the first picture to the server
    send_to_server(first_picture.to_json())

    # TEST_IMAGE_PATH = shop_path / "TEST_IMAGE.jpg"
    TEST_IMAGE_PATH = shop_path / first_picture.img_name
    print(f"[ DEBUG ] TEST_IMAGE_PATH: {TEST_IMAGE_PATH}")

    image = cv2.imread(TEST_IMAGE_PATH.as_posix())

    for item in first_picture.boxes:
        box = item["box"]
        color = COLOR_PALLETE[_id]
        # Create a rectangle around the object
        box_start_point = (int(box[0]), int(box[1]))  # left top corner
        box_end_point = (int(box[2]), int(box[3]))  # right bottom corner
        cv2.rectangle(img=image, pt1=box_start_point, pt2=box_end_point, color=color, thickness=2)


    # Save image
    cv2.imwrite(f"{first_picture.img_name}_OUTPUT.jpg", image)

    raise SystemExit

    # Resolve remaining xmls and assign IDs to the bounding boxes closes to the centroids
    previous_picture = first_picture
    for xml in xmls:
        current_picture = DataFrame(xml, shop_path)
        current_picture.assign_nearest_ids(previous_boxes=previous_picture.boxes)
        print(f"[ DEBUG ] current: {current_picture}")
        previous_picture = current_picture

        # Send the current picture to the server


def send_to_server(data: dict[str, Any]) -> None:
    """Send data to the server"""
    print(f"[ DEBUG ] data: {data}")
    response = requests.post(f"{API_BASE_URL}/post-test", json=data)
    print(f"[ DEBUG ] response: {response}")
    print(f"[ DEBUG ] response.text: {response.text}")


if __name__ == "__main__":
    main()