import logging
from nqrduck.module.module_model import ModuleModel
from nqrduck_spectrometer.base_spectrometer_model import BaseSpectrometerModel
from nqrduck_spectrometer.pulseparameters import Gate, TXPulse, RXReadout

logger = logging.getLogger(__name__)


class LimeNQRModel(BaseSpectrometerModel):

    def __init__(self, module) -> None:
        super().__init__(module)
        self.add_setting("Frequency", 100, "Experiment frequency", "Acquisition") 
        self.add_setting("Averages", 100, "Number of averages", "Acquisition")
        self.add_setting("Sampling Frequency", 30.72e6 , "Sampling frequency", "Acquisition")
        self.add_setting("IF Frequency", 1.2e6, "IF frequency", "Acquisition")
        self.add_setting("RX Gain", 55, "RX Gain", "RX/TX Settings")
        self.add_setting("TX Gain", 40, "TX Gain", "RX/TX Settings")
        self.add_setting("RX LPF BW", 30.72e6/2, "RX LPF BW", "RX/TX Settings")
        self.add_setting("TX LPF BW", 130.0e6, "TX LPF BW", "RX/TX Settings")
        self.add_pulse_parameter_option("TX", TXPulse)
        self.add_pulse_parameter_option("Gate", Gate)
        self.add_pulse_parameter_option("RX", RXReadout)

        try:
            from nqrduck_pulseprogrammer.pulseprogrammer import pulse_programmer
            self.pulse_programmer = pulse_programmer
            logger.debug("Pulse programmer found.")
            self.pulse_programmer.controller.on_loading(self.pulse_parameter_options)
        except ImportError:
            logger.warning("No pulse programmer found.")

    @property
    def rx_antenna(self):
        return self._rx_antenna
    
    @rx_antenna.setter
    def rx_antenna(self, value):
        self._rx_antenna = value

    @property
    def tx_antenna(self):
        return self._tx_antenna
    
    @tx_antenna.setter
    def tx_antenna(self, value):
        self._tx_antenna = value

    @property
    def rx_gain(self):
        return self._rx_gain

    @rx_gain.setter
    def rx_gain(self, value):
        self._rx_gain = value

    @property
    def tx_gain(self):
        return self._tx_gain
    
    @tx_gain.setter
    def tx_gain(self, value):
        self._tx_gain = value

    @property
    def rx_lpfbw(self):
        return self._rx_lpfbw
    
    @rx_lpfbw.setter
    def rx_lpfbw(self, value):
        self._rx_lpfbw = value

    @property
    def tx_lpfbw(self):
        return self._tx_lpfbw
    
    @tx_lpfbw.setter
    def tx_lpfbw(self, value):
        self._tx_lpfbw = value

    # Pulse params

    @property
    def tx_freq(self):
        return self._tx_freq
    
    @tx_freq.setter
    def tx_freq(self, value):
        self._tx_freq = value

