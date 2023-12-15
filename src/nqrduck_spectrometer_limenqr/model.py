import logging
from nqrduck_spectrometer.base_spectrometer_model import BaseSpectrometerModel
from nqrduck_spectrometer.pulseparameters import TXPulse, RXReadout

logger = logging.getLogger(__name__)


class LimeNQRModel(BaseSpectrometerModel):    
    # Setting constants for the names of the spectrometer settings
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
    RX_OFFSET = "RX offset"
    FFT_SHIFT = "FFT shift"

    # Constants for the Categories of the settings
    ACQUISITION = "Acquisition"
    GATE_SETTINGS = "Gate Settings"
    RX_TX_SETTINGS = "RX/TX Settings"
    CALIBRATION = "Calibration"
    SIGNAL_PROCESSING = "Signal Processing"

    # Pulse parameter constants
    TX = "TX"
    RX = "RX"

    # Settings that are not changed by the user
    OFFSET_FIRST_PULSE = 300
    

    def __init__(self, module) -> None:
        super().__init__(module)
        # Acquisition settings
        self.add_setting(self.SAMPLING_FREQUENCY, 30.72e6 , "Sampling frequency", self.ACQUISITION)
        self.add_setting(self.IF_FREQUENCY, 5e6, "IF Frequency", self.ACQUISITION)
        self.if_frequency = 1.2e6
        self.add_setting(self.ACQUISITION_TIME, 82e-6, "Acquisition time - this is from the beginning of the pulse sequence", self.ACQUISITION)
        # Gate Settings
        self.add_setting(self.GATE_ENABLE, True, "Enable", self.GATE_SETTINGS)
        self.add_setting(self.GATE_PADDING_LEFT, 10, "Gate padding left", self.GATE_SETTINGS)
        self.add_setting(self.GATE_PADDING_RIGHT, 10, "Gate padding right", self.GATE_SETTINGS)
        self.add_setting(self.GATE_SHIFT, 53, "Gate shift", self.GATE_SETTINGS)
        # RX/TX settings
        self.add_setting(self.RX_GAIN, 55, "RX Gain", self.RX_TX_SETTINGS)
        self.add_setting(self.TX_GAIN, 30, "TX Gain", self.RX_TX_SETTINGS)
        self.add_setting(self.RX_LPF_BW, 30.72e6/2, "RX LPF BW", self.RX_TX_SETTINGS)
        self.add_setting(self.TX_LPF_BW, 130.0e6, "TX LPF BW", self.RX_TX_SETTINGS)
        # Calibration settings
        self.add_setting(self.TX_I_DC_CORRECTION, -45, "TX I DC correction", self.CALIBRATION)
        self.add_setting(self.TX_Q_DC_CORRECTION, 0, "TX Q DC correction", self.CALIBRATION)
        self.add_setting(self.TX_I_GAIN_CORRECTION, 2047, "TX I Gain correction", self.CALIBRATION)
        self.add_setting(self.TX_Q_GAIN_CORRECTION, 2039, "TX Q Gain correction", self.CALIBRATION)
        self.add_setting(self.TX_PHASE_ADJUSTMENT, 3, "TX phase adjustment", self.CALIBRATION)
        self.add_setting(self.RX_I_DC_CORRECTION, 0, "RX I DC correction", self.CALIBRATION)
        self.add_setting(self.RX_Q_DC_CORRECTION, 0, "RX Q DC correction", self.CALIBRATION)
        self.add_setting(self.RX_I_GAIN_CORRECTION, 2047, "RX I Gain correction", self.CALIBRATION)
        self.add_setting(self.RX_Q_DC_CORRECTION, 2047, "TX Q Gain correction", self.CALIBRATION)
        self.add_setting(self.RX_PHASE_ADJUSTMENT, 0, "TX phase adjustment", self.CALIBRATION)
        # Signal Processing settings
        self.add_setting(self.RX_OFFSET, 2.4e-6, "The offset of the RX event, this changes all the time", self.SIGNAL_PROCESSING)
        self.add_setting(self.FFT_SHIFT, False, "FFT shift", self.SIGNAL_PROCESSING)

        # Pulse parameter options
        self.add_pulse_parameter_option(self.TX, TXPulse)
        # self.add_pulse_parameter_option(self.GATE, Gate)
        self.add_pulse_parameter_option(self.RX, RXReadout)

        # Try to load the pulse programmer module
        try:
            from nqrduck_pulseprogrammer.pulseprogrammer import pulse_programmer
            self.pulse_programmer = pulse_programmer
            logger.debug("Pulse programmer found.")
            self.pulse_programmer.controller.on_loading(self.pulse_parameter_options)
        except ImportError:
            logger.warning("No pulse programmer found.")

        self.averages = 1

    @property
    def target_frequency(self):
        return self._target_frequency
    
    @target_frequency.setter
    def target_frequency(self, value):
        self._target_frequency = value

    @property
    def averages(self):
        return self._averages
    
    @averages.setter
    def averages(self, value):
        self._averages = value

    @property
    def if_frequency(self):
        return self._if_frequency
    
    @if_frequency.setter
    def if_frequency(self, value):
        self._if_frequency = value


