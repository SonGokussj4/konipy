"""Main script file."""

from typing import Any
from pathlib import Path
from dataloader import load_images_from_dir, load_xml_from_dir, DataFrame

CURDIR = Path(__file__).parent

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
    print(f'[ DEBUG ] first: {first_picture}')

    # Send the first picture to the server

    # Resolve remaining xmls and assign IDs to the bounding boxes closes to the centroids
    previous_picture = first_picture
    for xml in xmls:
        current_picture = DataFrame(xml, shop_path)
        current_picture.assign_nearest_ids(previous_boxes=previous_picture.boxes)
        print(f'[ DEBUG ] current: {current_picture}')
        previous_picture = current_picture

        # Send the current picture to the server


if __name__ == "__main__":
    main()
