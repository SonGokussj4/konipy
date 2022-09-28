"""Main script file - Simple script"""

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from dataloader import load_images_from_dir, load_xml_from_dir, DataFrame

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

        TEST_IMAGE_PATH = shop_path / picture.img_name
        print(f"[ DEBUG ] TEST_IMAGE_PATH: {TEST_IMAGE_PATH}")

        image = cv2.imread(TEST_IMAGE_PATH.as_posix())

        for item in picture.boxes:
            box = item["box"]
            _id = item["id"]
            color = COLOR_PALLETE[_id]
            # Create a rectangle around the object
            box_start_point = (int(box[0]), int(box[1]))  # left top corner
            box_end_point = (int(box[2]), int(box[3]))  # right bottom corner
            cv2.rectangle(img=image, pt1=box_start_point, pt2=box_end_point, color=color, thickness=2)

            # Display ID of the box on the top of the rectangle
            label_text = f"ID: {_id}"

            # Get text size to know how long the "background rectangle" should be
            (text_box_x, text_box_y), _ = cv2.getTextSize(
                label_text, cv2.FONT_HERSHEY_SIMPLEX, LABEL_FONT_SCALE, LABEL_FONT_THICKNESS
            )

            label_x = box_start_point[0] + 5
            label_y = box_start_point[1] + 5

            # Create a rectangle around the text
            cv2.rectangle(
                img=image,
                pt1=(label_x - 5, label_y + 5),
                pt2=(label_x + text_box_x + 5, label_y - text_box_y - 5),
                color=color,
                thickness=cv2.FILLED,
            )

            # Display the text
            cv2.putText(
                img=image,
                text=label_text,
                org=(label_x, label_y),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=LABEL_FONT_SCALE,
                color=(0, 0, 0),
                thickness=LABEL_FONT_THICKNESS,
            )

        # Save image
        cv2.imwrite(f"{output_dir / picture.img_name}_OUTPUT.jpg", image)

    # Convert images to video
    images = [img for img in os.listdir(output_dir) if img.endswith("OUTPUT.jpg")]
    frame = cv2.imread(os.path.join(output_dir, images[0]))
    height, width, layers = frame.shape

    video_path = f"{output_dir}/video.mp4v"
    size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # desired codec (must be available at runtime)
    video = cv2.VideoWriter(video_path , fourcc, VIDEO_FPS, size)

    for image in images:
        video.write(cv2.imread(os.path.join(output_dir, image)))

    cv2.destroyAllWindows()
    video.release()

    raise SystemExit

    # Resolve remaining xmls and assign IDs to the bounding boxes closes to the centroids
    previous_picture = picture
    for xml in xmls:
        current_picture = DataFrame(xml, SHOP_DIR)
        current_picture.assign_nearest_ids(previous_boxes=previous_picture.boxes)
        print(f"[ DEBUG ] current: {current_picture}")
        previous_picture = current_picture

        # Send the current picture to the server



def send_picture(data: dict[str, Any]) -> None:
    """Send data to the server"""
    print(f"[ DEBUG ] data: {data}")
    response = requests.post(f"{API_BASE_URL}/post-test", json=data)
    if response.ok:
        print(f"[ DEBUG ] response.text: {response.text}")


if __name__ == "__main__":
    main()
