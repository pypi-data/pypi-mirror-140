import time
import os
from iot_gh.src.iot_gh.IoTGreenhouse import IoTGreenhouse
from airtable import Airtable

class GHWebService(object):
    """ Web connector for REST service. 
    Post data using json package.
    V2.1
    2/26/2022
    """
    POST_DELAY = 30     #Seconds between posts - throttle
    DATA_TABLE_NAME = 'GreenhouseData'
    DATA_TABLE_LOGS = 'GreenhouseLogs'
    
    def __init__(self, greenhouse:IoTGreenhouse):
        self.greenhouse = greenhouse
        api_key = os.environ['airtable_key']
        base_key = os.environ['airtable_iotgh_key']
        self._gh_data_table = Airtable(base_key, self.DATA_TABLE_NAME, api_key)
        self._gh_logs_table = Airtable(base_key, self.DATA_TABLE_LOGS, api_key)
        self.record_id = self.find_gh_record_id()
        self.last_post_time = 0
        
        # self.log_service = AppLogService(api_key, base_key)url, greenhouse_service):
        # self.gh_service = greenhouse_service
        # self.url = greenhouse_service._url
        
    def post_greenhouse(self):
        #throttle post to every 30 sec
        # gh = self.gh_service.greenhouse
        if time.time() > self.last_post_time + self.POST_DELAY:
            if not self.gh_is_valid():
                # log = AppLog(LOG_TYPE.ERROR, "Unable to add company name select. Company Name Select is None")
                # self.log_service.add_log(log)   
                pass
            else:
                try:
                    fields = self.get_fields()
                    if not self.record_id:
                        self._gh_data_table.insert(fields)
                    else:
                        self._gh_data_table.update({"id": self.record_id, "fields": fields})
                    self.last_post_time = time.time()
                except Exception as ex:
                    # log = AppLog(LOG_TYPE.ERROR, "Unable to add company. " + str(ex))
                    # self.log_service.add_log(log)
                    raise ex

    def gh_is_valid(self):
        return True

    def find_gh_record_id(self) -> str:
        "Return Company Name Select with specified name. Should be single record."
        records = self._gh_data_table.search('Name', self.greenhouse.name)
        if len(records) == 0:
            return ""
        elif len(records) == 1:
            return records["id"]
        else:
            # log = AppLog(LOG_TYPE.ERROR, "Duplicate Company Name records exist in Company Name Select.")
            # self.log_service.add_log(log)
            pass  

    def get_fields(self):
        fields = {"Name": self.greenhouse.name,
            "Temp In": self.greenhouse.temp_inside_F,
            "Temp Out": self.greenhouse.temp_outside_F,
            "Servo Status": self.greenhouse.servo_status,
            "Fan Status": self.greenhouse.fan_status,
            "Heater Status": self.greenhouse.led_white_status,  #white led simulates heater

            "Message": self.greenhouse.message}
        return fields

gh = IoTGreenhouse()
ws = GHWebService(gh)
ws.post_greenhouse()
