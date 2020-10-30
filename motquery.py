import sys
import json
import time
import requests

JSON_NAME_TO_KEY_MAPPING = {
    "Registration": "mispar_rechev",
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

INLINE_PRINT_FIELDS = ["Registration", "Chassis", "Color"]


def uniq(l, kf):
    uniqueKeys = set()
    result = []
    for item in l:
        if kf(item) not in uniqueKeys:
            uniqueKeys.add(kf(item))
            result.append(item)
    return result

def communicate(session, request):
    return session.send(request.prepare())

def generateJson(jsonDict):
    return json.dumps(jsonDict)

def generateHTTPRequest(filtersJson, count):
    return requests.Request(method="GET", url=f"https://data.gov.il/api/3/action/datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3&filters={filtersJson}&limit={count}&include_total=true")

def generateLicensePlateRequest(licensePlate):
    return generateHTTPRequest(generateJson({"mispar_rechev": licensePlate}), 1)

def generateMakeModelCodeRequest(makeCode, modelCode, count):
    return generateHTTPRequest(generateJson({"tozeret_cd": makeCode, "degem_cd": modelCode}), count)

def communicate(session, request):
    reply = None
    for retry in range(10):
        try:
            reply = session.send(request.prepare())
        except request.exceptions.ConnectionError:
            time.sleep(1)
            continue
        if reply.status_code == 200:
            break
        time.sleep(1)

    if not reply or reply.status_code != 200:
        return {}

    root = reply.json()
    return root["result"] if "result" in root else {}

def formatLicensePlate(licensePlate):
    if len(licensePlate) == 7:
        return f"{licensePlate[:2]}-{licensePlate[2:5]}-{licensePlate[5:]}"
    if len(licensePlate) == 8:
        return f"{licensePlate[:3]}-{licensePlate[3:5]}-{licensePlate[5:]}"

def formatPrint(jsonReply, fieldName, fieldKey):
    fieldValue = formatLicensePlate(str(jsonReply[fieldKey])) if fieldKey == "mispar_rechev" else jsonReply[fieldKey]
    print(f"\t{fieldName}: {fieldValue}")

def printVehicleDetails(jsonReply):
    print(f"*** Vehicle details for reg.# {jsonReply['mispar_rechev']} ***")
    for name, key in JSON_NAME_TO_KEY_MAPPING.items():
        formatPrint(jsonReply, name, key)
    print("")

def inlinePrintVehicleDetails(jsonReply):
    print(*[jsonReply[JSON_NAME_TO_KEY_MAPPING[field]] for field in INLINE_PRINT_FIELDS])


def searchByLicensePlate(session, licensePlate):
    licensePlateRequest = generateLicensePlateRequest(licensePlate)
    licensePlateReply = communicate(session, licensePlateRequest)
    printVehicleDetails(licensePlateReply["records"][0])

def searchByMakeModelCode(session, makeCode, modelCode):
    totalCountRequest = generateMakeModelCodeRequest(makeCode, modelCode, 0)
    totalCountReply = communicate(session, totalCountRequest)
    totalCount = totalCountReply["total"]

    allResultsRequest = generateMakeModelCodeRequest(makeCode, modelCode, totalCount)
    allResultsReply = communicate(session, allResultsRequest)
    allResults = allResultsReply["records"]
    

    print(f"\nFound {len(allResults)} unique results.")
    try:
        for result in sorted(allResults, key=lambda x: x["misgeret"]):
            inlinePrintVehicleDetails(result)
    except:
        pass


def main():
    if len(sys.argv) not in [2, 3] or not all(map(lambda x: x.isdigit(), sys.argv[1:])):
        print(f"Usage: {sys.argv[0]} <licensePlate> , or")
        print(f"       {sys.argv[0]} <makeCode> <modelCode>")
        return

    session = requests.Session()

    if len(sys.argv) == 2:
        searchByLicensePlate(session, int(sys.argv[1]))
    elif len(sys.argv) == 3:
        searchByMakeModelCode(session, int(sys.argv[1]), int(sys.argv[2]))

if __name__ == "__main__":
    main()
