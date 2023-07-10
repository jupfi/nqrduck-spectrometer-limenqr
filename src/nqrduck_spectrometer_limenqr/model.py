import logging
from nqrduck.module.module_model import ModuleModel
from nqrduck_spectrometer.base_spectrometer_model import BaseSpectrometerModel

logger = logging.getLogger(__name__)


class LimeNQRModel(BaseSpectrometerModel):

    def __init__(self, module) -> None:
        super().__init__(module)
        self.add_setting("RX Gain", 55, "RX Gain")
        self.add_setting("TX Gain", 40, "TX Gain")
        self.add_pulse_parameter_option("tx_pulse", [self.RectPulse, self.SincPulse, self.GaussianPulse])
        self.add_pulse_parameter_option("rx_readout", [self.RXReadout])
        self.add_pulse_parameter_option("gate", [self.Gate])

        try:
            from nqrduck_pulseprogrammer.pulseprogrammer import pulse_programmer
            self.pulse_programmer = pulse_programmer
            logger.debug("Pulse programmer found.")
            self.pulse_programmer.controller.on_loading(self.pulse_parameter_options)
        except ImportError:
            logger.warning("No pulse programmer found.")

    class TXPulse(BaseSpectrometerModel.PulseParameter):
        def __init__(self, name) -> None:
            super().__init__(name)
            self.tx_freq = 0
            self.tx_phase = 0

    class RectPulse(TXPulse):
        def __init__(self, name) -> None:
            super().__init__(name)
  
    class SincPulse(TXPulse):
        def __init__(self, name) -> None:
            super().__init__(name)

    class GaussianPulse(TXPulse):
        def __init__(self, name) -> None:
            super().__init__(name)

    class RXReadout(BaseSpectrometerModel.PulseParameter):
        def __init__(self, name) -> None:
            super().__init__(name)
            self.rx_freq = 0
            self.rx_phase = 0

    class Gate(BaseSpectrometerModel.PulseParameter):
        def __init__(self, name) -> None:
            super().__init__(name)
            self.state = False

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

