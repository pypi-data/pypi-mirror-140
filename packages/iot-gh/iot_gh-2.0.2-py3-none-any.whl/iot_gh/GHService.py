import datetime
from iot_gh.src.iot_gh.GHgpio import GHgpio
from iot_gh.src.iot_gh.GHAnalogService import GHAnalogService
from iot_gh.src.iot_gh.GHBuzzer import GHBuzzer
from iot_gh.src.iot_gh.GHFan import GHFan
from iot_gh.src.iot_gh.GHLamps import GHLamps
from iot_gh.src.iot_gh.GHServo import GHServo
from iot_gh.src.iot_gh.GHSwitches import GHSwitches
from iot_gh.src.iot_gh.GHTemperature import GHTemperature
from iot_gh.src.iot_gh.GHWebService import GHWebService
from iot_gh.src.iot_gh.IoTGreenhouse import IoTGreenhouse

class GHService(object):
    """A container class for IoT Greenhouse services.
    
    Provides references to component services.
    """
    
    # _pi = None      #pigpio connection
    # _spi = None
    # _url = None
    # _servo_ccw_limit = None
    # _servo_cw_limit = None
    
    # greenhouse = None
    # version = None
    
    # analog_service = None
    # ain_pot = None
    # ain_temp = None
    # ain_light = None
    # ain_aux = None
    # buzzer = None
    # fan = None
    # lamps = None
    # servo = None
    # switches = None
    # temperature = None
    # web_service = None

    def __init__(self, pi, spi):
        """Initializes an IoT Greenhouse container.
        """
        self._pi = pi
        self._spi = spi

        if not self._pi.connected:
            raise Exception("ERROR: unable to connect to pigpio")
        
        #self._read_config()
        self._make_components()
        # self.greenhouse = IoTGreenhouse()
        # self.update_greenhouse()

    # def _read_config(self):
    #     """Loads configuration file from user iot_gh directory.
    #     """
    #     try:
    #         config = configparser.ConfigParser()
            
    #         # if type(self._pi) is : #debug mode. Load test file
    #         #    config.read("./iot_gh_system.conf")
    #         # else:
    #         #     config.read(["iot_gh_system.conf", os.path.expanduser("~/.iot_gh/iot_gh_system.conf")],encoding="UTF8")
    #         self.version = config["IOT_GREENHOUSE"]["VERSION"]
    #         # self._url = config["IOT_GREENHOUSE"]["URL"]
    #         self._servo_ccw_limit = int(config["IOT_GREENHOUSE"]["SERVO_CCW_LIMIT"])
    #         self._servo_cw_limit = int(config["IOT_GREENHOUSE"]["SERVO_CW_LIMIT"])
    #     except Exception as ex:
    #         raise Exception("Unable to load IoT Greenhouse System Configuration. %s" % ex.args[0])
       
    def _make_components(self):
        """Makes component services for IoT Greenhouse container.
        """
        self.analog = GHAnalogService(self._pi, self._spi)
        self.buzzer = GHBuzzer(self._pi, GHgpio.BUZZER)
        self.fan = GHFan(self._pi, GHgpio.FAN)
        self.lamps = GHLamps(self._pi, GHgpio.RED_LED, GHgpio.WHITE_LED, GHgpio.RED_LED, GHgpio.DUAL_LED)
        self.servo = GHServo(self._pi, GHgpio.SERVO_PWM, self._servo_cw_limit, self._servo_ccw_limit)
        self.switches = GHSwitches(self._pi, GHgpio.SWITCH_PB, GHgpio.SWITCH_TOGGLE)
        self.temperature = GHTemperature(self.analog.aux, self.analog.temp)
        self.web_service = GHWebService(self)    
        
    # def _make_greenhouse(self, name=""):
    #     """Factory class to build IoT Greenhouse data object.
    #     """
    #     gh = IoTGreenhouse(name)
        
    #     #read greenhouse config values
    #     config = configparser.ConfigParser()
    #     if type(self._pi) is not pigpio.pi: #debug mode. Load test file
    #         config.read("./iot_gh.conf")
    #     else:
    #         config.read(["iot_gh.conf", os.path.expanduser("~/.iot_gh/iot_gh.conf")],encoding="UTF8")
    #     gh.house_id = config["IOT_GREENHOUSE"]["HOUSE_ID"]
    #     gh.group_id = config["IOT_GREENHOUSE"]["GROUP_ID"]
    #     gh.house_number = config["IOT_GREENHOUSE"]["HOUSE_NUMBER"].zfill(2)
    #     gh.version = self.version

    #     return gh
    
    def update_greenhouse(self, greenhouse:IoTGreenhouse ):
        """Updates IoTGreenhouse object by reading all house 
        states and refreshing gh object.
        """
        try:
    
            greenhouse.led_red_state = self.lamps.red.get_state()
            greenhouse.led_red_status = self.lamps.red.get_status()
            greenhouse.led_white_state = self.lamps.white.get_state()
            greenhouse.led_white_status = self.lamps.white.get_status()
            greenhouse.led_dual_state =  self.lamps.dual.get_state()
            greenhouse.led_dual_status = self.lamps.dual.get_status()
            greenhouse.switch_pb_state = self.switches.push_button.get_state()
            greenhouse.switch_pb_status = self.switches.push_button.get_status()
            greenhouse.switch_toggle_state = self.switches.toggle.get_state()
            greenhouse.switch_toggle_status = self.switches.toggle.get_status()
            greenhouse.fan_state =  self.fan.get_state()
            greenhouse.fan_status =  self.fan.get_status()
            greenhouse.servo_position = self.servo.get_value()
            greenhouse.servo_status = self.servo.get_status()
            greenhouse.heater_state = self.lamps.white.get_state()
            greenhouse.heater_status = self.lamps.white.get_status()
            greenhouse.buzzer_state = self.buzzer.get_state()
            greenhouse.buzzer_status = self.buzzer.get_status()
            greenhouse.ain_pot_raw = self.analog.pot.get_value()
            greenhouse.ain_light_raw =  self.analog.light.get_value()
            greenhouse.ain_aux_raw =  self.analog.aux.get_value()

            greenhouse.temp_inside_C = self.temperature.get_inside_temp_C()
            greenhouse.temp_inside_F = self.temperature.get_inside_temp_F()
            greenhouse.temp_outside_C = self.temperature.get_outside_temp_C()
            greenhouse.temp_outside_F = self.temperature.get_outside_temp_F()
            
            greenhouse.last_update = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
            
            self._make_message(greenhouse)
            

        except Exception as e:
            greenhouse.message = "Update exception: %s" % e.args[0]
            
    def _make_message(self, gh:IoTGreenhouse):
        m = ""
        if  gh.temp_outside_C > gh.temp_inside_C: 
            m = "Warning: The temperature outside the greenhouse is higher than the internal temperature."
        elif gh.servo_status == "CLOSED" and gh.fan_status == "ON":
            m = "Error: The fan is activated by louvers are closed."
        else:
            m = "Greenhouse status is normal."

        gh.message = m