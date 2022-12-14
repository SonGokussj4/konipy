"""Main script file - FastAPI app"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

import uvicorn
import cv2
from fastapi import FastAPI, Response, HTTPException, Request

from loguru import logger as log
from logger_config import init_logging

# Load environment variables
load_dotenv()

DEBUG = os.getenv("DEBUG", str(False))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
HOT_RELOAD = os.getenv("HOT_RELOAD", str(False))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", "8989")

# CONSTANTS
# Paths
CURDIR = Path(__file__).parent
SHOP_DIR = CURDIR / "shop"
# Drawing and video
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


if DEBUG == "True":
    HOST = "localhost"
    SHOP_DIR = CURDIR.parent / "shop"



app = FastAPI(title="Visualising API", description="API for visualising data", version="0.1.0")

init_logging()



@app.get("/", status_code=200, include_in_schema=False)
def read_root():
    return Response("The API is working")


@app.post("/mark-pictures")
async def mark_pictures(data: Request) -> Response:
    """Test POST request"""
    picture = await data.json()
    img_name = Path(picture.get("img_name"))
    img_path = SHOP_DIR / img_name.name
    log.debug(f"img_path: {img_path}")

    image = cv2.imread(img_path.as_posix())

    for item in picture.get("boxes"):
        box = item["box"]
        _id = item["id"]
        # centroid = item["centroid"]
        previous_centroids = item["previous_centroids"]
        color = COLOR_PALLETE[_id]

        draw_bounding_box(image, box, color)
        draw_label(image, box, _id, color)
        draw_centroids(image, previous_centroids, color)
        draw_line(image, previous_centroids, color)

    # Save image
    output_img_path = f"{SHOP_DIR / img_name.stem}_OUTPUT.jpg"
    log.debug(f"output_img_path: {output_img_path}")
    cv2.imwrite(output_img_path, image)

    return Response(
        content=json.dumps({"output_path": output_img_path, "name": Path(output_img_path).stem, "message": "ok"}),
        media_type="application/json",
    )


@app.post("/message")
async def message(data: Request) -> Response:
    """Get message"""
    _data = await data.json()
    msg = _data.get("message", "")

    if msg.lower() == "finished":
        log.info("Received message: finished")
        response = create_video()
        return response

    return Response(content=json.dumps({"message": "no message received"}), media_type="application/json")


def create_video():
    """Create video from images"""
    # Convert images to video
    log.debug("Creating video...")
    images = [img for img in os.listdir(SHOP_DIR) if img.endswith("OUTPUT.jpg")]
    frame = cv2.imread(os.path.join(SHOP_DIR, images[0]))
    height, width, _ = frame.shape

    video_path = f"{SHOP_DIR}/video.mp4v"
    size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # desired codec (must be available at runtime)
    video = cv2.VideoWriter(video_path, fourcc, VIDEO_FPS, size)

    for image in images:
        img_path = os.path.join(SHOP_DIR, image)
        video.write(cv2.imread(img_path))

    cv2.destroyAllWindows()
    video.release()

    log.info(f"Video created: {video_path}")

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


def draw_centroids(image, centroids, color):
    """Draw centroid on the image"""
    for centroid in centroids:
        cv2.circle(img=image, center=(int(centroid[0]), int(centroid[1])), radius=3, color=color, thickness=-1)

def draw_line(image, centroids, color):
    """Draw line on the image"""
    for i in range(len(centroids) - 1):
        cv2.line(
            img=image,
            pt1=(int(centroids[i][0]), int(centroids[i][1])),
            pt2=(int(centroids[i + 1][0]), int(centroids[i + 1][1])),
            color=color,
            thickness=2,
        )



if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=int(PORT), log_level=LOG_LEVEL, reload=bool(HOT_RELOAD))
