from decimal import Decimal
import requests_async as requests

BATTERY_SOC_PERCENT_ENDPOINT = "items/SPPro_BattSocPercent"

POWER_USED_WATTS_ENDPOINT = "items/SPPro_PowerUsed"
EXPORT_POWER_WATTS_ENDPOINT = "items/SPPro_ExportPower"
AC_LOAD_POWER_WATTS_ENDPOINT = "items/SPPro_LoadAcPower"

EXPORT_KILOWATT_HOURS_ENDPOINT = "items/SPPro_ExportkWhAcc"
AC_LOAD_KILOWATT_HOURS_ENDPOINT = "items/SPPro_ACLoadkWhAcc"
AC_INPUT_KILOWATT_HOURS_ENDPOINT = "items/SPPro_ACInputkWhAcc"

BATTERY_INPUT_KILLOWATT_HOURS_ENDPOINT = "items/SPPro_BattInkWhAcc"
BATTERY_OUTPUT_KILLOWATT_HOURS_ENDPOINT = "items/SPPro_BattOutkWhAcc"

class ArvioEmaxxReader():
    """Instance of ArvioEmaxxReader"""

    def __init__(self, host):
        self._host = host.lower()
        self._endpoint_root = f"http://{self._host}:8080/rest/"

    async def battery_soc_percent(self):
        return await self.get_decimal(BATTERY_SOC_PERCENT_ENDPOINT)


    async def power_used_watts(self):
        return await self.get_decimal(POWER_USED_WATTS_ENDPOINT)

    async def export_power_watts(self):
        return await self.get_decimal(EXPORT_POWER_WATTS_ENDPOINT)

    async def ac_load_power_watts(self):
        return await self.get_decimal(AC_LOAD_POWER_WATTS_ENDPOINT)


    async def export_kilowatt_hours(self):
        return await self.get_decimal(EXPORT_KILOWATT_HOURS_ENDPOINT)

    async def ac_load_kilowatt_hours(self):
        return await self.get_decimal(AC_LOAD_KILOWATT_HOURS_ENDPOINT)

    async def ac_input_kilowatt_hours(self):
        return await self.get_decimal(AC_INPUT_KILOWATT_HOURS_ENDPOINT)

    async def battery_input_kilowatt_hours(self):
        return await self.get_decimal(BATTERY_INPUT_KILLOWATT_HOURS_ENDPOINT)

    async def battery_output_kilowatt_hours(self):
        return await self.get_decimal(BATTERY_OUTPUT_KILLOWATT_HOURS_ENDPOINT)
    

    async def get_decimal(self, endpoint):
        response_json = await self.call_api(endpoint)
        return Decimal(response_json["state"])

    async def call_api(self, endpoint):
        """Method to call the Arvio API"""
        response = await requests.get(self._endpoint_root + endpoint, timeout=10, allow_redirects=False,
                                      headers={'Accept': 'application/json'})
        return response.json()
