import logging
from pathlib import Path
import numpy as np
from nqrduck.module.module_controller import ModuleController
from nqrduck_spectrometer.base_spectrometer_controller import BaseSpectrometerController

logger = logging.getLogger(__name__)

class LimeNQRController(BaseSpectrometerController):
    def __init__(self, module):
        super().__init__(module)

    def start_measurement(self):
        logger.debug("Starting measurement with spectrometer: %s", self.module.model.name)
        # Now we request the pulse sequence set in the pulse programmer module
        pulse_sequence = self.module.model.pulse_programmer.model.pulse_sequence
        logger.debug("Pulse sequence is: %s", pulse_sequence.dump_sequence_data())

        try:
           from .contrib.limr import limr
           self_path = Path(__file__).parent
           driver_path = str(self_path / "contrib/pulseN_test_USB.cpp")
           lime = limr(driver_path)
        except ImportError as e:
            logger.error("Error while importing limr. %s", e)
        except Exception as e:
            logger.error("Error while loading pulseN_test_USB.cpp: %s", e)

        lime = self.update_settings(lime)
        lime = self.translate_pulse_sequence(lime)

    def update_settings(self, lime):
        logger.debug("Updating settings for spectrometer: %s for measurement", self.module.model.name)
        l.t3d = [0, 0, 0, 0]
        for category in self.module.model.settings.keys():
            for setting in self.module.model.settings[category]:
                logger.debug("Setting %s has value %s", setting.name, setting.value)
                if setting.name == "RX Gain":
                    lime.rgn = setting.value
                elif setting.name == "TX Gain":
                    lime.tgn = setting.value
                elif setting.name == "Averages":
                    lime.nav = setting.value
                elif setting.name == "Sampling Frequency":
                    lime.sra = setting.value
                elif setting.name == "RX LPF BW":
                    lime.rlp = setting.value
                elif setting.name == "TX LPF BW":
                    lime.tlp = setting.value
                elif setting.name == "IF frequency":
                    lime.lof = self.target_frequency - setting.value
                elif setting.name == "Acquisition time":
                    lime.tac = 82e-6
                elif setting.name == "Enable":
                    lime.t3d[0] = int(setting.value)
                elif setting.name == "Gate padding left":
                    lime.t3d[1] = setting.value
                elif setting.name == "Gate shift":
                    lime.t3d[2] = setting.value
                elif setting.name == "Gate padding right":
                    lime.t3d[3] = setting.value
                
        return lime

    def translate_pulse_sequence(self, lime):
        """This method translates the pulse sequence into the format required by the lime spectrometer.
        """

        for event in self.module.model.pulse_programmer.model.pulse_sequence.events.values():
            logger.debug("Event %s has parameters: %s", event.name, event.parameters)
            for parameter in event.parameters.values():
                logger.debug("Parameter %s has options: %s", parameter.name, parameter.options)
            
                if parameter.name == "TX":
                    
                    if len(lime.pfr) == 0:
                        # Add the TX pulse to the pulse frequency list (lime.pfr)
                        lime.pfr = [self.module.model.if_frequency]
                        # Add the duration of the TX pulse to the pulse duration list (lime.pdr)
                        lime.pdr = [event.duration]
                        # Add the TX pulse amplitude to the pulse amplitude list (lime.pam)
                        lime.pam = [parameter.options["TX Amplitude"].value]
                        # Add the pulse offset to the pulse offset list (lime.pof)
                        # This leads to a default offset of 300 samples for the first pulse
                        lime.pof = [300]
                        # Add the TX pulse phase to the pulse phase list (lime.pph) -> not yet implemented
                    else:
                        lime.pfr.append(self.module.model.if_frequency)
                        lime.pdr.append(event.duration)
                        lime.pam.append(parameter.options["TX Amplitude"].value)
                        lime.pof.append(np.ceil(lime.pfr[-2] * lime.sra))         

            # The acquisition time can be calculated from the buffer length of 4096 samples and the sampling frequency
            # 82µs is the shortest possible acquisition time

            # The last event is the repetition time event
            lime.trp = event.duration
        
        lime.npu = len(lime.pfr)
        return lime
        