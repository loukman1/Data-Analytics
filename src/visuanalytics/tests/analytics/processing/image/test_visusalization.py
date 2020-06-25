import os
import shutil
import unittest

from visuanalytics.analytics.control.procedures.step_data import StepData
from visuanalytics.analytics.processing.image.visualization import generate_all_images
from visuanalytics.analytics.util import resources


def prepare_image_test(values, data, config=None):
    if config is None:
        config = {}

    step_data = StepData(config, "1")
    step_data.init_data({"_test": data})
    values = {"images": values,
              "presets": {
                  "test_preset": {
                      "color": "black",
                      "font_size": 20,
                      "font": "Test_Font.ttf"
                  }}}
    step_data.data["_pipe_id"] = "102"
    generate_all_images(values, step_data, True)

    return values["images"]


class PreprocessTest(unittest.TestCase):
    os.makedirs(resources.get_temp_resource_path("", "102", True), exist_ok=True)

    def test_single_image(self):
        values = {
            "test_1": {
                "type": "pillow",
                "path": "Test_Bild_2.png",
                "overlay": [
                    {
                        "type": "text",
                        "anchor_point": "left",
                        "pos_x": 200,
                        "pos_y": 50,
                        "preset": "test_preset",
                        "pattern": "{_req|_test|test_1}"
                    }
                ]
            }
        }
        data = {
            "test_1": "Test text"
        }
        expected = prepare_image_test(values, data)
        assert os.path.exists(resources.get_resource_path(expected["test_1"])) == 1

    def test_multiple_images(self):
        values = {
            "test_1": {
                "type": "pillow",
                "path": "Test_Bild_2.png",
                "overlay": [
                    {
                        "type": "text",
                        "anchor_point": "left",
                        "pos_x": 200,
                        "pos_y": 50,
                        "preset": "test_preset",
                        "pattern": "{_req|_test|test_1}"
                    }
                ]
            },
            "test_2": {
                "type": "pillow",
                "already_created": True,
                "path": "test_1",
                "overlay": [
                    {
                        "type": "text",
                        "anchor_point": "left",
                        "pos_x": 200,
                        "pos_y": 50,
                        "preset": "test_preset",
                        "pattern": "{_req|_test|test_1}"
                    }
                ]
            }
        }
        data = {
            "test_1": "Test text"
        }
        expected = prepare_image_test(values, data)
        assert os.path.exists(resources.get_resource_path(expected["test_2"])) == 1

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(resources.get_temp_resource_path("", "102", True), ignore_errors=True)
