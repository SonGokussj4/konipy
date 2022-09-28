"""Main script file - Simple script"""

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from dataloader import load_xml_from_dir, DataFrame

# LOAD ENVIROMENT VARIABLES
load_dotenv()

DEBUG = os.getenv("DEBUG")
if DEBUG == "True":
    API_BASE_URL = "http://localhost:8989"
else:
    API_BASE_URL = os.getenv("API_BASE_URL", "")

# CONSTANTS
CURDIR = Path(__file__).parent
PARENT_DIR = CURDIR.parent
SHOP_DIR = PARENT_DIR / "shop"


def main():
    """Main function."""
    xmls = load_xml_from_dir((SHOP_DIR / "*.xml").as_posix())
    xmls = xmls[:2]

    for idx, xml in enumerate(xmls):
        # Assign random IDs to the bounding boxes in first xml
        picture = DataFrame(xml, SHOP_DIR)
        picture.assign_ids()

        # Send the first picture to the server
        send_picture(picture.to_json())

        # if last picture, send message to the server
        if idx == len(xmls) - 1:
            send_message(message="finished")

    raise SystemExit

    # Resolve remaining xmls and assign IDs to the bounding boxes closes to the centroids
    previous_picture = picture
    for xml in xmls:
        current_picture = DataFrame(xml, SHOP_DIR)
        current_picture.assign_nearest_ids(previous_boxes=previous_picture.boxes)
        print(f"[ DEBUG ] current: {current_picture}")
        previous_picture = current_picture

        # Send the current picture to the server


def send_message(message: str) -> None:
    """Send message to the server"""
    response = requests.post(f"{API_BASE_URL}/message", json={"message": message})
    if response.ok:
        print(f"[ DEBUG ] response.text: {response.text}")


def send_picture(data: dict[str, Any]) -> None:
    """Send data to the server"""
    print(f"[ DEBUG ] data: {data}")
    response = requests.post(f"{API_BASE_URL}/post-test", json=data)
    if response.ok:
        print(f"[ DEBUG ] response.text: {response.text}")


if __name__ == "__main__":
    main()
