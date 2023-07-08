import logging
from nqrduck.module.module_controller import ModuleController
from nqrduck_spectrometer.base_spectrometer_controller import BaseSpectrometerController

logger = logging.getLogger(__name__)

class LimeNQRController(BaseSpectrometerController):
    def __init__(self, module):
        super().__init__(module)

    def start_measurement(self):
        logger.debug("Starting measurement with spectrometer: %s", self.module.model.name)
