import sys
import json
import time
import argparse
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


def communicate(session, request):
    return session.send(request.prepare())

def generateJson(jsonDict):
    return json.dumps(jsonDict)

def generateHTTPRequest(filtersJson, count):
    return requests.Request(method="GET", url=f"https://data.gov.il/api/3/action/datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3&filters={filtersJson}&limit={count}&include_total=true")

def generateLicensePlateRequest(licensePlate):
    return generateHTTPRequest(generateJson({"mispar_rechev": licensePlate}), 1)

def generateRequestByParams(params, count):
    return generateHTTPRequest(generateJson(params), count)

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
    # print(jsonReply)
    print("")

def inlinePrintVehicleDetails(jsonReply, inlinePrintFields=INLINE_PRINT_FIELDS):
    print(*[jsonReply[JSON_NAME_TO_KEY_MAPPING[field]] for field in inlinePrintFields])


def searchByLicensePlate(session, licensePlate):
    licensePlateRequest = generateLicensePlateRequest(licensePlate)
    licensePlateReply = communicate(session, licensePlateRequest)
    printVehicleDetails(licensePlateReply["records"][0])

def baseSearchAll(session, searchParams, extraPrintFields=[]):
    totalCountRequest = generateRequestByParams(searchParams, 0)
    totalCountReply = communicate(session, totalCountRequest)
    totalCount = totalCountReply["total"]

    allResultsRequest = generateRequestByParams(searchParams, totalCount)
    allResultsReply = communicate(session, allResultsRequest)
    allResults = allResultsReply["records"]

    print(f"\nFound {len(allResults)} unique results.")
    try:
        for result in sorted(allResults, key=lambda x: x["misgeret"]):
            inlinePrintVehicleDetails(result, INLINE_PRINT_FIELDS + extraPrintFields)
    except:
        pass


def searchByMakeModelCode(session, makeCode, modelCode):
    params = {"tozeret_cd": makeCode, "degem_cd": modelCode}
    baseSearchAll(session, params)

def searchByModelName(session, modelName):
    params = {"degem_nm": modelName}
    baseSearchAll(session, params, ["Manufacturer number", "Model number"])


def main():
    parser = argparse.ArgumentParser("MoTQuery")
    parser.add_argument("-l", "--licenseplate", dest="licensePlate", help="License plate")
    parser.add_argument("-M", "--makecode", dest="makeCode", help="Make code")
    parser.add_argument("-m", "--modelcode", dest="modelCode", help="Model code")
    parser.add_argument("-n", "--modelname", dest="modelName", help="Model name")
    
    args = parser.parse_args()

    if args.licensePlate and (args.makeCode or args.modelCode or args.modelName):
        print("-l cannot be used in conjunction with other flags. Exiting")
        return

    if args.modelName and (args.makeCode or args.modelCode or args.licensePlate):
        print("-n cannot be used in conjunction with other flags. Exiting")
        return

    session = requests.Session()

    if args.licensePlate:
        searchByLicensePlate(session, int(args.licensePlate))
    elif args.modelName:
        searchByModelName(session, args.modelName)
    elif args.makeCode and args.modelCode:
        searchByMakeModelCode(session, int(args.makeCode), int(args.modelCode))
    else:
        print(f"{'-m' if args.makeCode else '-M'} missing, exiting")

if __name__ == "__main__":
    main()
