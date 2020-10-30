import sys
import json
import time
import requests


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

def main():
    if len(sys.argv) != 3 or not sys.argv[1].isdigit() or not sys.argv[2].isdigit():
        print(f"Usage: {sys.argv[0]} <manufacturer#> <model#>")
        return

    session = requests.Session()
    filtersJson = json.dumps({"tozeret_cd": int(sys.argv[1]), "degem_cd": int(sys.argv[2])})

    totalCountReply = communicate(session, requests.Request(method="GET", url=f"https://data.gov.il/api/3/action/datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3&filters={filtersJson}&limit=0&include_total=true"))
    totalCount = totalCountReply.json()["result"]["total"]

    allResultsReply = communicate(session, requests.Request(method="GET", url=f"https://data.gov.il/api/3/action/datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3&filters={filtersJson}&limit={totalCount}"))
    allResults = allResultsReply.json()["result"]["records"]
    

    print(f"\nFound {len(allResults)} unique results.")
    try:
        for result in sorted(allResults, key=lambda x: x["misgeret"]):
            print(result["mispar_rechev"], result["misgeret"], result["tzeva_rechev"])
    except:
        pass

if __name__ == "__main__":
    main()
