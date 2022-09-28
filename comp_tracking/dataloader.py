"""Handler functions and class to manage data """
from pathlib import Path
import glob
import xml.etree.ElementTree as ET

import cv2
import numpy as np


class DataFrame:
    """DataFrame class

    Encapsulate data about image and bounding boxes.
    """

    def __init__(self, xml: str, path: str):
        self.img_name, self.boxes = self._extract_info(xml)
        self.img = self._load_image(path)

    def _extract_info(self, xml):
        tree = ET.parse(xml)
        root = tree.getroot()

        boxes = []

        for obj in root.iter("object"):
            img_name = root.find("filename").text

            ymin, xmin, ymax, xmax = None, None, None, None

            ymin = int(obj.find("bndbox/ymin").text)
            xmin = int(obj.find("bndbox/xmin").text)
            ymax = int(obj.find("bndbox/ymax").text)
            xmax = int(obj.find("bndbox/xmax").text)

            box = (xmin, ymin, xmax, ymax)

            # Compute centroid
            centroid = ((xmin + xmax) / 2, (ymin + ymax) / 2)

            boxes.append({"id": None, "box": box, "centroid": centroid})

        return img_name, boxes

    def _load_image(self, path):
        img_path = str((Path(path) / self.img_name).resolve())
        img = cv2.imread(img_path)
        return img

    def _compute_distance(self, centroid1, centroid2):
        return np.linalg.norm(np.array(centroid1) - np.array(centroid2))

    def assign_ids(self):
        """Assign random IDs to the bounding boxes"""
        # for box in self.boxes:
        #     box['id'] = np.random.randint(0, 1000)
        for idx, box in enumerate(self.boxes):
            box["id"] = idx

    def assign_nearest_ids(self, previous_boxes):
        """Assign IDs to the bounding boxes closes to the centroids"""
        for box in self.boxes:
            # Compute distance to all centroids
            distances = []
            for previous_box in previous_boxes:
                distance = self._compute_distance(previous_box["centroid"], box["centroid"])
                distances.append(distance)

            # Assign the ID of the closest centroid
            box["id"] = previous_boxes[np.argmin(distances)]["id"]

    def to_json(self):
        return {"img_name": self.img_name, "boxes": self.boxes}

    def __repr__(self):
        return f"DataFrame(" f"img_name={self.img_name}, " f"boxes={self.boxes}" ")"


def load_images_from_dir(path):
    """Load images from the path to list"""
    imgs = [{"img": cv2.imread(file), "filename": str(file)} for file in glob.glob(path)]
    return imgs


def load_xml_from_dir(path: str) -> list[str]:
    """Load sorted xml files to list"""
    xml_files = sorted([file for file in glob.glob(path)])
    return xml_files


if __name__ == "__main__":
    path_xml = "shop/*.xml"
    xmls = load_xml_from_dir(path_xml)
