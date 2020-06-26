import json
import logging
import os
import shutil
import time

from visuanalytics.analytics.apis.api import api
from visuanalytics.analytics.control.procedures.step_data import StepData
from visuanalytics.analytics.processing.audio.audio import generate_audios
from visuanalytics.analytics.processing.image.visualization import generate_all_images
from visuanalytics.analytics.sequence.sequence import link
from visuanalytics.analytics.transform.transform import transform
from visuanalytics.analytics.util import resources
from visuanalytics.analytics.util.storing import storing

logger = logging.getLogger(__name__)


class Pipeline(object):
    """Enthält alle informationen zu einer Pipeline, und führt alle Steps aus.

    Benötigt beim Ersttellen eine id, und eine Instanz der Klasse :class:`Steps` bzw. einer Unterklasse von :class:`Steps`.
    Bei dem Aufruf von Start werden alle Steps der Reihe nach ausgeführt.
    """
    __steps = {-2: {"name": "Error"},
               -1: {"name": "Not Started"},
               0: {"name": "Apis", "call": api},
               1: {"name": "Transform", "call": transform},
               2: {"name": "Storing", "call": storing},
               3: {"name": "Images", "call": generate_all_images},
               4: {"name": "Audios", "call": generate_audios},
               5: {"name": "Sequence", "call": link},
               6: {"name": "Ready"}}
    __steps_max = 6

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
        """float: Startzeit der Pipeline. Wird erst bei dem Aufruf von :func:`start` inizalisiert."""
        return self.__start_time

    @property
    def end_time(self):
        """float: Endzeit der Pipeline. Wird erst nach Beendigung der Pipeline inizalisiert."""
        return self.__end_time

    @property
    def id(self):
        """str: id der Pipeline."""
        return self.__id

    def progress(self):
        """Fortschritt der Pipeline.

        :return: Anzahl der schon ausgeführten schritte, Anzahl aller Schritte
        :rtype: int, int
        """
        return self.__current_step + 1, self.__steps_max + 1

    def current_step_name(self):
        """Gibt den Namen des aktuellen Schritts zurück.

        :return: Name des Aktuellen Schrittes.
        :rtype: str
        """
        return self.__steps[self.__current_step]["name"]

    def __setup(self):
        logger.info(f"Initializing Pipeline {self.id}...")

        # Load json config file
        with resources.open_resource(f"steps/{self.__step_name}.json") as fp:
            self.__config = json.loads(fp.read())

        os.mkdir(resources.get_temp_resource_path("", self.id))

    def __cleanup(self):
        # delete Directory
        logger.info("Cleaning up...")
        shutil.rmtree(resources.get_temp_resource_path("", self.id), ignore_errors=True)
        logger.info("Finished cleanup!")

    def start(self):
        """Führt alle Schritte die in der übergebenen Instanz der Klasse :class:`Steps` definiert sind aus.

        Initalisiertt zuerst einen Pipeline Ordner mit der Pipeline id, dieser kann dann im gesamten Pipeline zur
        zwichenspeicherung von dateien verwendet werden. Dieser wird nach Beendigung oder bei einem Fehler fall wieder gelöscht.

        Führt alle Schritte aus der übergebenen Steps instans, die in der Funktion :func:`sequence` difiniert sind,
        der reihnfolge nach aus. Mit der ausnahme von allen Steps mit der id < 0 und >= `step_max`.

        :return: Wenn ohne fehler ausgeführt `True`, sonst `False`
        :rtype: bool
        """
        try:
            self.__setup()
            data = StepData(self.steps_config, self.id)

            self.__start_time = time.time()
            logger.info(f"Pipeline {self.id} started!")

            for self.__current_step in range(0, self.__steps_max):
                logger.info(f"Next step: {self.current_step_name()}")

                # Execute Step
                self.__steps[self.__current_step].get("call", lambda: None)(self.__config, data)

                logger.info(f"Step finished: {self.current_step_name()}!")

            # Set state to ready
            self.__current_step = self.__steps_max

            self.__end_time = time.time()
            completion_time = round(self.__end_time - self.__start_time, 2)
            logger.info(f"Pipeline {self.id} finished in {completion_time}s")

            self.__cleanup()
            return True

        except Exception:
            self.__current_step = -2
            logger.exception(f"An error occurred: ")
            logger.info(f"Pipeline {self.id} could not be finished.")
            self.__cleanup()
            return False
