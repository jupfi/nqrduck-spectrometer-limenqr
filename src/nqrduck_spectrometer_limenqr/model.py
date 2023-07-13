import logging
from nqrduck.module.module_model import ModuleModel
from nqrduck_spectrometer.base_spectrometer_model import BaseSpectrometerModel
from nqrduck_spectrometer.pulseparameters import Gate, TXPulse, RXReadout

logger = logging.getLogger(__name__)


class LimeNQRModel(BaseSpectrometerModel):

    def __init__(self, module) -> None:
        super().__init__(module)
        # Acquisition settings
        self.add_setting("Frequency", 100e6, "Experiment frequency", "Acquisition")
        self.target_frequency = 100e6 
        self.add_setting("Averages", 100, "Number of averages", "Acquisition")
        self.add_setting("Sampling Frequency", 30.72e6 , "Sampling frequency", "Acquisition")
        self.add_setting("IF Frequency", 1.2e6, "IF frequency", "Acquisition")
        self.if_frequency = 1.2e6
        self.add_setting("Acquisition time", 82e-6, "Acquisition time - this is from the beginning of the pulse sequence", "Acquisition")
        # Gate Settings
        self.add_setting("Enable", True, "Enable", "Gate Settings")
        self.add_setting("Gate padding left", 10, "Gate padding left", "Gate Settings")
        self.add_setting("Gate padding right", 10, "Gate padding right", "Gate Settings")
        self.add_setting("Gate shift", 53, "Gate shift", "Gate Settings")
        # RX/TX settings
        self.add_setting("RX Gain", 55, "RX Gain", "RX/TX Settings")
        self.add_setting("TX Gain", 40, "TX Gain", "RX/TX Settings")
        self.add_setting("RX LPF BW", 30.72e6/2, "RX LPF BW", "RX/TX Settings")
        self.add_setting("TX LPF BW", 130.0e6, "TX LPF BW", "RX/TX Settings")
        # Calibration settings
        self.add_setting("TX I DC correction", -45, "TX I DC correction", "Calibration")
        self.add_setting("TX Q DC correction", 0, "TX Q DC correction", "Calibration")
        self.add_setting("TX I Gain correction", 2047, "TX I Gain correction", "Calibration")
        self.add_setting("TX Q Gain correction", 2039, "TX Q Gain correction", "Calibration")
        self.add_setting("TX phase adjustment", 3, "TX phase adjustment", "Calibration")
        self.add_setting("RX I DC correction", 0, "TX I DC correction", "Calibration")
        self.add_setting("RX Q DC correction", 0, "TX Q DC correction", "Calibration")
        self.add_setting("RX I Gain correction", 2047, "TX I Gain correction", "Calibration")
        self.add_setting("RX Q Gain correction", 2047, "TX Q Gain correction", "Calibration")
        self.add_setting("RX phase adjustment", 0, "TX phase adjustment", "Calibration")

        # Pulse parameter options
        self.add_pulse_parameter_option("TX", TXPulse)
        self.add_pulse_parameter_option("Gate", Gate)
        self.add_pulse_parameter_option("RX", RXReadout)

        # Try to load the pulse programmer module
        try:
            from nqrduck_pulseprogrammer.pulseprogrammer import pulse_programmer
            self.pulse_programmer = pulse_programmer
            logger.debug("Pulse programmer found.")
            self.pulse_programmer.controller.on_loading(self.pulse_parameter_options)
        except ImportError:
            logger.warning("No pulse programmer found.")

    @property
    def target_frequency(self):
        return self._target_frequency
    
    @target_frequency.setter
    def target_frequency(self, value):
        self._target_frequency = value

    @property
    def if_frequency(self):
        return self._if_frequency
    
    @if_frequency.setter
    def if_frequency(self, value):
        self._if_frequency = value


