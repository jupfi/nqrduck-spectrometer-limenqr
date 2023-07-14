import logging
from nqrduck.module.module_model import ModuleModel
from nqrduck_spectrometer.base_spectrometer_model import BaseSpectrometerModel
from nqrduck_spectrometer.pulseparameters import Gate, TXPulse, RXReadout

logger = logging.getLogger(__name__)


class LimeNQRModel(BaseSpectrometerModel):
    
    # Setting constants for the names of the spectrometer settings
    FREQUENCY = "Frequency"
    AVERAGES = "Averages"
    SAMPLING_FREQUENCY = "Sampling Frequency"
    IF_FREQUENCY = "IF Frequency"
    ACQUISITION_TIME = "Acquisition time"
    GATE_ENABLE = "Enable"
    GATE_PADDING_LEFT = "Gate padding left"
    GATE_PADDING_RIGHT = "Gate padding right"
    GATE_SHIFT = "Gate shift"
    RX_GAIN = "RX Gain"
    TX_GAIN = "TX Gain"
    RX_LPF_BW = "RX LPF BW"
    TX_LPF_BW = "TX LPF BW"
    TX_I_DC_CORRECTION = "TX I DC correction"
    TX_Q_DC_CORRECTION = "TX Q DC correction"
    TX_I_GAIN_CORRECTION = "TX I Gain correction"
    TX_Q_GAIN_CORRECTION = "TX Q Gain correction"
    TX_PHASE_ADJUSTMENT = "TX phase adjustment"
    RX_I_DC_CORRECTION = "RX I DC correction"
    RX_Q_DC_CORRECTION = "RX Q DC correction"
    RX_I_GAIN_CORRECTION = "RX I Gain correction"
    RX_Q_GAIN_CORRECTION = "RX Q Gain correction"
    RX_PHASE_ADJUSTMENT = "RX phase adjustment"

    def __init__(self, module) -> None:
        super().__init__(module)
        # Acquisition settings
        self.add_setting(self.FREQUENCY, 100e6, "Experiment frequency", "Acquisition")
        self.target_frequency = 100e6 
        self.add_setting(self.AVERAGES, 100, "Number of averages", "Acquisition")
        self.add_setting(self.SAMPLING_FREQUENCY, 30.72e6 , "Sampling frequency", "Acquisition")
        self.add_setting(self.IF_FREQUENCY, 1.2e6, "IF Frequency", "Acquisition")
        self.if_frequency = 1.2e6
        self.add_setting(self.ACQUISITION_TIME, 82e-6, "Acquisition time - this is from the beginning of the pulse sequence", "Acquisition")
        # Gate Settings
        self.add_setting(self.GATE_ENABLE, True, "Enable", "Gate Settings")
        self.add_setting(self.GATE_PADDING_LEFT, 10, "Gate padding left", "Gate Settings")
        self.add_setting(self.GATE_PADDING_RIGHT, 10, "Gate padding right", "Gate Settings")
        self.add_setting(self.GATE_SHIFT, 53, "Gate shift", "Gate Settings")
        # RX/TX settings
        self.add_setting(self.RX_GAIN, 55, "RX Gain", "RX/TX Settings")
        self.add_setting(self.TX_GAIN, 40, "TX Gain", "RX/TX Settings")
        self.add_setting(self.RX_LPF_BW, 30.72e6/2, "RX LPF BW", "RX/TX Settings")
        self.add_setting(self.TX_LPF_BW, 130.0e6, "TX LPF BW", "RX/TX Settings")
        # Calibration settings
        self.add_setting(self.TX_I_DC_CORRECTION, -45, "TX I DC correction", "Calibration")
        self.add_setting(self.TX_Q_DC_CORRECTION, 0, "TX Q DC correction", "Calibration")
        self.add_setting(self.TX_I_GAIN_CORRECTION, 2047, "TX I Gain correction", "Calibration")
        self.add_setting(self.TX_Q_GAIN_CORRECTION, 2039, "TX Q Gain correction", "Calibration")
        self.add_setting(self.TX_PHASE_ADJUSTMENT, 3, "TX phase adjustment", "Calibration")
        self.add_setting(self.RX_I_DC_CORRECTION, 0, "RX I DC correction", "Calibration")
        self.add_setting(self.RX_Q_DC_CORRECTION, 0, "RX Q DC correction", "Calibration")
        self.add_setting(self.RX_I_GAIN_CORRECTION, 2047, "RX I Gain correction", "Calibration")
        self.add_setting(self.RX_Q_DC_CORRECTION, 2047, "TX Q Gain correction", "Calibration")
        self.add_setting(self.RX_PHASE_ADJUSTMENT, 0, "TX phase adjustment", "Calibration")

        # Pulse parameter options
        self.add_pulse_parameter_option("TX", TXPulse)
        # self.add_pulse_parameter_option("Gate", Gate)
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


