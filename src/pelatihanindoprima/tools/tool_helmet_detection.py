from typing import Type

from pydantic import BaseModel, Field

from crewai.tools import BaseTool

from ultralytics import YOLO
import json


class Tool_helmet_detection_input(BaseModel):
    """Input schema for MyCustomTool."""

    # argument: str = Field(..., description="location file.")
    image: str = Field(..., description="path atau url gambar")


class Tool_helmet_detection(BaseTool):
    name: str = "Tool helmet detection"
    description: str = "Tool latihan untuk deteksi helm."
    args_schema: Type[BaseModel] = Tool_helmet_detection_input

    modelYolo: YOLO = YOLO("src/pelatihanindoprima/tools/model_yolo.pt")

    def _run(self, image: str) -> str:
        result = self.modelYolo(image)
        detected_objects = result[0].boxes.cls.tolist()
        class_names = result[0].names
        # object_counts = {}
        person = 0
        helmet = 0
        head = 0

        for hasil in detected_objects:
            class_name = class_names[int(hasil)]
            if (class_name == "head"):
                head = head + 1
            elif (class_name == "helmet"):
                helmet = helmet + 1
            else:
                person = person + 1

        result_dict = {
            "result": f"Detected {person} person(s), {helmet} helmet(s), {head} head(s) without helmet",
            "head": head,
            "person": person,
            "helmet": helmet
        }

        return str(result_dict)
