"""Main script file - Simple script"""

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from dataloader import load_xml_from_dir, DataFrame

# LOAD ENVIROMENT VARIABLES
load_dotenv()

# CONSTANTS
CURDIR = Path(__file__).parent
SHOP_DIR = CURDIR / "shop"

DEBUG = os.getenv("DEBUG")
if DEBUG == "True":
    API_BASE_URL = "http://localhost:8989"
    SHOP_DIR = CURDIR.parent / "shop"
else:
    API_BASE_URL = os.getenv("API_BASE_URL", "")


def main():
    """Main function."""
    xmls = load_xml_from_dir((SHOP_DIR / "*.xml").as_posix())

    previous_picture = None
    for idx, xml in enumerate(xmls):
        current_picture = DataFrame(xml, SHOP_DIR)

        # Assign random IDs to the bounding boxes in first xml
        if idx == 0:
            current_picture.assign_ids()
        else:
            # print("[ DEBUG ] previous_picture: ", previous_picture)
            assert previous_picture is not None
            current_picture.assign_nearest_ids(previous_boxes=previous_picture.boxes)

        previous_picture = current_picture

        # Send the first picture to the server
        send_picture(current_picture.to_json())

        # if last picture, send message to the server
        if idx == len(xmls) - 1:
            send_message(message="finished")

    return 0


def send_message(message: str) -> None:
    """Send message to the server"""
    response = requests.post(f"{API_BASE_URL}/message", json={"message": message})
    if response.ok:
        print(f"[ DEBUG ] response.text: {response.text}")


def send_picture(data: dict[str, Any]) -> None:
    """Send data to the server"""
    print(f"[ DEBUG ] data: {data}")
    response = requests.post(f"{API_BASE_URL}/mark-pictures", json=data)
    if response.ok:
        print(f"[ DEBUG ] response.text: {response.text}")


if __name__ == "__main__":
    main()
