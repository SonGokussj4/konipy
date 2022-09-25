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
    print(f'first_picture: {first_picture}')

    # Send the first picture to the server

    # Resolve remaining xmls and assign IDs to the bounding boxes closes to the centroids
    for xml in xmls:
        df = DataFrame(xml, shop_path)
        df.assign_nearest_ids(fist_picture_boxes=first_picture.boxes)

if __name__ == "__main__":
    main()
