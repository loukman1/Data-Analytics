import json
import logging
import os
import shutil
import time

from visuanalytics.analytics.apis.api import api, api_request
from visuanalytics.analytics.control.procedures.step_data import StepData
from visuanalytics.analytics.processing.audio.audio import generate_audios
from visuanalytics.analytics.processing.image.visualization import generate_all_images
from visuanalytics.analytics.sequence.sequence import link
from visuanalytics.analytics.storing.storing import storing
from visuanalytics.analytics.transform.transform import transform
from visuanalytics.analytics.thumbnail.thumbnail import thumbnail
from visuanalytics.analytics.util.video_delete import delete_amount_videos, delete_fix_name_videos
from visuanalytics.util import resources
from visuanalytics.util.resources import get_current_time

logger = logging.getLogger(__name__)


class Pipeline(object):
    """Enthält alle Informationen zu einer Pipeline und führt alle Steps aus.

    Benötigt beim Erstellen eine id und eine Instanz der Klasse :class:`Steps` bzw. einer Unterklasse von :class:`Steps`.
    Bei dem Aufruf von Start werden alle Steps der Reihe nach ausgeführt.
    """
    __steps = {-2: {"name": "Error"},
               -1: {"name": "Not Started"},
               0: {"name": "Apis", "call": api},
               1: {"name": "Transform", "call": transform},
               2: {"name": "Storing", "call": storing},
               3: {"name": "Images", "call": generate_all_images},
               4: {"name": "Thumbnail", "call": thumbnail},
               5: {"name": "Audios", "call": generate_audios},
               6: {"name": "Sequence", "call": link},
               7: {"name": "Ready"}}
    __steps_max = 7

    def __init__(self, pipeline_id: str, step_name: str, steps_config=None):
        if steps_config is None:
            steps_config = {}

        self.__step_name = step_name
        self.steps_config = steps_config
        self.__start_time = 0.0
        self.__end_time = 0.0
        self.__id = pipeline_id
        self.__config = {}
        self.__current_step = -1

    @property
    def start_time(self):
        """float: Startzeit der Pipeline. Wird erst bei dem Aufruf von :func:`start` initialisiert."""
        return self.__start_time

    @property
    def end_time(self):
        """float: Endzeit der Pipeline. Wird erst nach Beendigung der Pipeline initialisiert."""
        return self.__end_time

    @property
    def id(self):
        """str: id der Pipeline."""
        return self.__id

    def progress(self):
        """Fortschritt der Pipeline.

        :return: Anzahl der schon ausgeführten Schritte, Anzahl aller Schritte.
        :rtype: int, int
        """
        return self.__current_step + 1, self.__steps_max + 1

    def current_step_name(self):
        """Gibt den Namen des aktuellen Schritts zurück.

        :return: Name des aktuellen Schritts.
        :rtype: str
        """
        return self.__steps[self.__current_step]["name"]

    def __setup(self):
        logger.info(f"Initializing Pipeline {self.id}...")

        # Load json config file
        with resources.open_resource(f"steps/{self.__step_name}.json") as fp:
            self.__config = json.loads(fp.read())

        os.mkdir(resources.get_temp_resource_path("", self.id))

        logger.info(f"Inizalization finished!")

    @staticmethod
    def __on_completion(data: StepData):
        cp_request = data.get_config("on_completion")

        # IF ON Completion is in config send Request
        if cp_request is not None:
            try:
                logger.info("Send completion notice...")

                # Make request
                api_request(cp_request, data, "", True)

                logger.info("Completion report sent out!")
            except Exception:
                logger.exception("Completion report could not be sent: ")

    def __cleanup(self):
        # delete Directory
        logger.info("Cleaning up...")
        shutil.rmtree(resources.get_temp_resource_path("", self.id), ignore_errors=True)

        if self.steps_config.get("keep_count", -1) > 0 and self.steps_config.get("fix_names", None) is None:
            delete_amount_videos(self.steps_config["job_name"], self.steps_config["output_path"],
                                 self.steps_config["keep_count"])
        logger.info("Finished cleanup!")

    def start(self):
        """Führt alle Schritte, die in der übergebenen Instanz der Klasse :class:`Steps` definiert sind, aus.

        Initialisiert zuerst einen Pipeline-Ordner mit der Pipeline id. Dieser kann dann in der gesamten Pipeline zur
        Zwichenspeicherung von Dateien verwendet werden. Dieser wird nach Beendigung oder bei einem Fehlerfall wieder gelöscht.

        Führt alle Schritte aus der übergebenen Steps Instanz, die in der Funktion :func:`sequence` definiert sind,
        der Reihenfolge nach aus. Mit der Ausnahme von allen Steps mit der id < 0 und >= `step_max`.

        :return: Wenn ohne Fehler ausgeführt `True`, sonst `False`
        :rtype: bool
        """
        try:
            self.__setup()
            data = StepData(self.steps_config, self.id)

            self.__config["out_time"] = get_current_time()
            self.__start_time = time.time()
            logger.info(f"Pipeline {self.id} started!")

            for self.__current_step in range(0, self.__steps_max):
                logger.info(f"Next step: {self.current_step_name()}")

                # Execute Step
                self.__steps[self.__current_step].get("call", lambda: None)(self.__config, data)

                logger.info(f"Step finished: {self.current_step_name()}!")

            # Set state to ready
            self.__current_step = self.__steps_max

            if self.steps_config.get("fix_names", None) is not None:
                fix_names = []
                if self.steps_config["fix_names"].get("names", None) is None:
                    for i in range(1, self.steps_config["fix_names"].get("count", 3) + 1):
                        fix_names.append(f"_{i}")
                else:
                    fix_names = self.steps_config["fix_names"]["names"]
                delete_fix_name_videos(self.steps_config["job_name"], fix_names,
                                       self.steps_config["output_path"], self.__config)
            self.__end_time = time.time()
            completion_time = round(self.__end_time - self.__start_time, 2)
            logger.info(f"Pipeline {self.id} finished in {completion_time}s")

            self.__on_completion(data)
            self.__cleanup()
            return True

        except Exception:
            self.__current_step = -2
            logger.exception(f"An error occurred: ")
            logger.info(f"Pipeline {self.id} could not be finished.")
            self.__cleanup()
            return False
