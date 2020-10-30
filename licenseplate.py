import sys
import json
import time
import requests

JSON_NAME_TO_KEY_MAPPING = {
    "Manufacturer": "tozeret_nm",
    "Model": "kinuy_mishari",
    "Trim": "ramat_gimur",
    "Model year": "shnat_yitzur",
    "Model code": "degem_nm",
    "Chassis": "misgeret",
    "Last MOT date": "mivchan_acharon_dt",
    "Color": "tzeva_rechev",
    "Manufacturer number": "tozeret_cd",
    "Model number": "degem_cd",
}

class CarRegistrationDetails:
    def __init__(self):
        self.session = requests.Session()

    def generateHTTPRequest(self, query, offset=0):
        filtersJson = json.dumps({"mispar_rechev": query})
        return requests.Request(method="GET", url=f"https://data.gov.il/api/3/action/datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3&filters={filtersJson}&offset={offset}")

    def formatPrint(self, jsonReply, fieldName, fieldKey):
        print(f"\t{fieldName}: {jsonReply[fieldKey]}")

    def printVehicleDetails(self, jsonReply):
        print(f"*** Vehicle details for reg.# {jsonReply['mispar_rechev']} ***")
        for name, key in JSON_NAME_TO_KEY_MAPPING.items():
            self.formatPrint(jsonReply, name, key)
        print("")

    def fetchVehicleDetails(self, regNumber):
        while True:
            request = self.generateHTTPRequest(regNumber)
            try:
                reply = self.session.send(request.prepare())
            except request.exceptions.ConnectionError:
                time.sleep(1)
                continue
            if reply.status_code == 200:
                break
            time.sleep(1)
        root = reply.json()
        return root["result"]["records"][0] if "result" in root and root["result"]["records"] else {}

    def search(self, regNumber, verbose=True):
        jsonReply = self.fetchVehicleDetails(regNumber)
        if verbose and jsonReply:
            self.printVehicleDetails(jsonReply)
        return jsonReply
   
def main():
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        print(f"Usage: {sys.argv[0]} <registration #>")
        return
    crd = CarRegistrationDetails()
    crd.search(sys.argv[1])


if __name__ == "__main__":
    main()
