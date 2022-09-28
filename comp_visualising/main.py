"""Main script file - FastAPI app"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

import uvicorn
import cv2
from fastapi import FastAPI, Response, HTTPException, Request

from loguru import logger as log
from logger_config import init_logging

# CONSTANTS
CURDIR = Path(__file__).parent
PARENT_DIR = CURDIR.parent
SHOP_DIR = PARENT_DIR / "shop"
LABEL_FONT_SCALE = 0.5
LABEL_FONT_THICKNESS = 1
VIDEO_FPS = 5
# Color pallete - BGR format (OpenCV)
COLOR_PALLETE = {
    0: (0, 0, 255),
    1: (0, 255, 0),
    2: (0, 255, 255),
    3: (255, 0, 255),
    4: (255, 255, 0),
    5: (255, 0, 0),
}





app = FastAPI(title="Visualising API", description="API for visualising data", version="0.1.0")

init_logging()



@app.get("/", status_code=200, include_in_schema=False)
def read_root():
    return Response("The API is working")


@app.post("/post-test")
async def post_test(data: Request) -> Response:
    """Test POST request"""
    picture = await data.json()

    IMAGE_PATH = SHOP_DIR / picture.get("img_name")
    log.debug(f"IMAGE_PATH: {IMAGE_PATH}")

    image = cv2.imread(IMAGE_PATH.as_posix())

    for item in picture.get("boxes"):
        box = item["box"]
        _id = item["id"]
        color = COLOR_PALLETE[_id]

        draw_bounding_box(image, box, color)
        draw_label(image, box, _id, color)

    # Save image
    image_path = f"{SHOP_DIR / picture.get('img_name')}_OUTPUT.jpg"
    cv2.imwrite(image_path, image)

    return Response(
        content=json.dumps({"output_path": image_path, "name": Path(image_path).stem, "message": "ok"}),
        media_type="application/json",
    )


@app.post("/message")
async def message(data: Request) -> Response:
    """Get message"""
    _data = await data.json()
    msg = _data.get("message", "")

    if msg.lower() == "finished":
        response = create_video()
        return response

    return Response(content=json.dumps({"message": "no message received"}), media_type="application/json")


def create_video():
    """Create video from images"""
    # Convert images to video
    images = [img for img in os.listdir(SHOP_DIR) if img.endswith("OUTPUT.jpg")]
    frame = cv2.imread(os.path.join(SHOP_DIR, images[0]))
    height, width, _ = frame.shape

    video_path = f"{SHOP_DIR}/video.mp4v"
    size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # desired codec (must be available at runtime)
    video = cv2.VideoWriter(video_path, fourcc, VIDEO_FPS, size)

    for image in images:
        video.write(cv2.imread(os.path.join(SHOP_DIR, image)))

    cv2.destroyAllWindows()
    video.release()

    return Response(content=json.dumps({"video_path": video_path, "name": Path(video_path).stem, "message": "ok"}))


def draw_bounding_box(image, box, color):
    """Draw bounding box on the image"""
    box_start_point = (int(box[0]), int(box[1]))  # left top corner
    box_end_point = (int(box[2]), int(box[3]))  # right bottom corner
    cv2.rectangle(img=image, pt1=box_start_point, pt2=box_end_point, color=color, thickness=2)


def draw_label(image, box, _id, color):
    """Draw label on the image"""
    # Display ID of the box on the top of the rectangle
    label_text = f"ID: {_id}"

    # Get text size to know how long the "background rectangle" should be
    (text_box_x, text_box_y), _ = cv2.getTextSize(
        label_text, cv2.FONT_HERSHEY_SIMPLEX, LABEL_FONT_SCALE, LABEL_FONT_THICKNESS
    )

    label_x = int(box[0]) + 5
    label_y = int(box[1]) + 5

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


