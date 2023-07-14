import logging
import tempfile
from scipy.fftpack import fft, fftshift, fftfreq
import matplotlib.pyplot as plt
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

        
        lime.noi = -1 # No initialisation
        lime.nrp = 1 # Numer of repetitions

        lime = self.update_settings(lime)
        lime = self.translate_pulse_sequence(lime)

        for key in sorted(lime.parsinp):
            val = getattr(lime, key)
            if val != []:
                # logger.debug("Attribute: %s, Value: %s, Descr.: %s" % key, val, lime.parsinp[key][1])
                logger.debug(key + ": " + str(val) + " " + lime.parsinp[key][1])
        
        # Create temp folder for .hdf files
        temp_dir = tempfile.TemporaryDirectory()
        path = Path(temp_dir.name)
        logger.debug("Created temporary directory: %s", path)
        lime.spt = path
        lime.fpa = "temp"

        logger.debug("Starting measurement")
        lime.run()

        logger.debug("Reading hdf file")
        lime.readHDF()

        rx_begin, rx_stop = self.translate_rx_event(lime)
        logger.debug("RX event starts at: %s and ends at: %s", rx_begin, rx_stop)

        #evaluation range, defines: blanking time and window length
        evran = [rx_begin, rx_stop]
        
        #np.where sometimes does not work out, so it is put in a try except
        #always check the console for errors
        try:
            evidx = np.where( (lime.HDF.tdx > evran[0]) & (lime.HDF.tdx < evran[1]) )[0]
        except:
            print("error due to np.where evaluation!")
        
        #time domain x and y data    
        tdx = lime.HDF.tdx[evidx]
        tdy = lime.HDF.tdy[evidx]

        #correcting a offset in the time domain by subtracting the mean
        tdy_mean = tdy[:,0]-np.mean(tdy)
            
        #fft of the corrected time domain data
        fdy1 = fftshift(fft(tdy_mean,axis=0),axes=0)

        #fft freq and fft shift is here used to scale the x axis (frequency axis)
        fdx1 = fftfreq(len(fdy1))*lime.sra/1e6
        fdx1 = fftshift(fdx1)

        #scaling factor which converts the y axis (usually a proportional number of points) into uV
        fac_p_to_uV = 447651/1e6
        
        #tdy_mean = tdy_mean/l.nav/fac_p_to_uV/RX_gainfactor
        
        
        plt.figure(1);
        plt.plot(tdx,tdy_mean/lime.nav)
        plt.xlabel("t in µs")
        plt.ylabel("Amplitude / points")
        plt.show()

    def update_settings(self, lime):
        logger.debug("Updating settings for spectrometer: %s for measurement", self.module.model.name)
        lime.t3d = [0, 0, 0, 0]
        for category in self.module.model.settings.keys():
            for setting in self.module.model.settings[category]:
                logger.debug("Setting %s has value %s", setting.name, setting.value)
                # Acquisiton settings
                if setting.name == self.module.model.FREQUENCY:
                    self.module.model.target_frequency = setting.get_setting()
                elif setting.name == self.module.model.AVERAGES:
                    lime.nav = setting.get_setting()
                elif setting.name == self.module.model.SAMPLING_FREQUENCY:
                    lime.sra = setting.get_setting()
                # Careful this doesn't only set the IF frequency but the local oscillator frequency
                elif setting.name == self.module.model.IF_FREQUENCY:
                    lime.lof = self.module.model.target_frequency - setting.get_setting()
                    self.module.model.if_frequency = setting.get_setting()
                elif setting.name == self.module.model.ACQUISITION_TIME:
                    lime.tac = setting.get_setting()
                # Gate settings
                elif setting.name == self.module.model.GATE_ENABLE:
                    lime.t3d[0] = int(setting.value)
                elif setting.name == self.module.model.GATE_PADDING_LEFT:
                    lime.t3d[1] = int(setting.get_setting())
                elif setting.name == self.module.model.GATE_SHIFT:
                    lime.t3d[2] = int(setting.get_setting())
                elif setting.name == self.module.model.GATE_PADDING_RIGHT:
                    lime.t3d[3] = int(setting.get_setting())
                # RX/TX settings
                elif setting.name == self.module.model.TX_GAIN:
                    lime.tgn = setting.get_setting()
                elif setting.name == self.module.model.RX_GAIN:
                    lime.rgn = setting.get_setting()
                elif setting.name == self.module.model.RX_LPF_BW:
                    lime.rlp = setting.get_setting()
                elif setting.name == self.module.model.TX_LPF_BW:
                    lime.tlp = setting.get_setting()
                # Calibration settings
                elif setting.name == self.module.model.TX_I_DC_CORRECTION:
                    lime.tdi = setting.get_setting()
                elif setting.name == self.module.model.TX_Q_DC_CORRECTION:
                    lime.tdq = setting.get_setting()
                elif setting.name == self.module.model.TX_I_GAIN_CORRECTION:
                    lime.tgi = setting.get_setting()
                elif setting.name == self.module.model.TX_Q_GAIN_CORRECTION:
                    lime.tgq = setting.get_setting()
                elif setting.name == self.module.model.TX_PHASE_ADJUSTMENT:
                    lime.tpc = setting.get_setting()
                elif setting.name == self.module.model.RX_I_DC_CORRECTION:
                    lime.rdi = setting.get_setting()
                elif setting.name == self.module.model.RX_Q_DC_CORRECTION:
                    lime.rdq = setting.get_setting()
                elif setting.name == self.module.model.RX_I_GAIN_CORRECTION:
                    lime.rgi = setting.get_setting()
                elif setting.name == self.module.model.RX_Q_GAIN_CORRECTION:
                    lime.rgq = setting.get_setting()
                elif setting.name == self.module.model.RX_PHASE_ADJUSTMENT:
                    lime.rpc = setting.get_setting()
                
        return lime

    def translate_pulse_sequence(self, lime):
        """This method sets the parameters of the limr object according to the pulse sequence set in the pulse programmer module#
        This is only relevant for the tx pulse parameters. General settings are set in the update_settings method and the rx event is 
        handled in the translate_rx_event method.

        Args:
            lime (limr): The limr object that is used to communicate with the pulseN driver
        
        Returns:
            limr: The updated limr object
        """
        events = self.module.model.pulse_programmer.model.pulse_sequence.events

        for event in events:
            logger.debug("Event %s has parameters: %s", event.name, event.parameters)
            for parameter in event.parameters.values():
                logger.debug("Parameter %s has options: %s", parameter.name, parameter.options)
            
                if parameter.name == self.module.model.TX and parameter.options["TX Amplitude"].value > 0:
                    
                    if len(lime.pfr) == 0:
                        # Add the TX pulse to the pulse frequency list (lime.pfr)
                        lime.pfr = [float(self.module.model.if_frequency)]
                        # Add the duration of the TX pulse to the pulse duration list (lime.pdr)
                        lime.pdr = [float(event.duration)]
                        # Add the TX pulse amplitude to the pulse amplitude list (lime.pam)
                        lime.pam = [float(parameter.options["TX Amplitude"].value)]
                        # Add the pulse offset to the pulse offset list (lime.pof)
                        # This leads to a default offset of 300 samples for the first pulse
                        lime.pof = [self.module.model.OFFSET_FIRST_PULSE]
                        # Add the TX pulse phase to the pulse phase list (lime.pph) -> not yet implemented
                    else:
                        logger.debug("Adding TX pulse to existing pulse sequence")
                        logger.debug("Setting if frequency to: %s", self.module.model.if_frequency)
                        lime.pfr.append(float(self.module.model.if_frequency))
                        logger.debug("Setting pulse duration to: %s", event.duration)
                        lime.pdr.append(float(event.duration))
                        logger.debug("Setting pulse amplitude to: %s", parameter.options["TX Amplitude"].value)
                        lime.pam.append(float(parameter.options["TX Amplitude"].value))
                        # Get the length of the previous event without a tx pulse
                        blank = []
                        previous_events = events[:events.index(event)]
                        # Firstuful this is ugly as hell and needs to be refactored
                        # Secondly this just sets the pulse offsets.
                        for prev_event in previous_events[::-1]:
                            logger.debug("Previous event: %s with duration: %s", prev_event.name, prev_event.duration)
                            for parameter in prev_event.parameters.values():
                                if parameter.name == self.module.model.TX and parameter.options["TX Amplitude"].value == 0:
                                    blank.append(float(prev_event.duration))
                                elif parameter.name == self.module.model.TX and parameter.options["TX Amplitude"].value > 0:
                                    break
                            else:
                                continue
                            break
                        
                        logger.debug("Found blanks: %s", blank)

                        prev_duration = lime.pdr[-2] + sum(blank)
                        
                        logger.debug("Setting pulse offset to: %s", prev_duration)
                        lime.pof.append(np.ceil(prev_duration * lime.sra))         

    
            # The last event is the repetition time event
            lime.trp = float(event.duration)
        
        lime.npu = len(lime.pfr)
        return lime
    
    def translate_rx_event(self, lime):
        # This is a correction factor for the RX event. The offset of the first pulse is 2.2µs longer than from the specified samples.
        CORRECTION_FACTOR = 2.2e-6  
        events = self.module.model.pulse_programmer.model.pulse_sequence.events

        for event in events:
            logger.debug("Event %s has parameters: %s", event.name, event.parameters)
            for parameter in event.parameters.values():
                logger.debug("Parameter %s has options: %s", parameter.name, parameter.options)
            
                if parameter.name == self.module.model.RX and parameter.options['RX'].state:
                    # Get the length of all previous events
                    previous_events = events[:events.index(event)]
                    previous_events_duration = sum([event.duration for event in previous_events])
                    # Get the offset of the first pulse
                    offset = self.module.model.OFFSET_FIRST_PULSE * (1/lime.sra)
                    rx_duration = event.duration
        
        rx_begin = previous_events_duration + offset + CORRECTION_FACTOR
        rx_stop = rx_begin + rx_duration

        return rx_begin * 1e6, rx_stop * 1e6
                    
        