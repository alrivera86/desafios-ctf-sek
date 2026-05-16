import requests

INTERNAL_API = "http://internal-api:8080/api/v1/zigbee/send"
TARGET_LOCK_NWK = "0x7B9C"


def process_zigbee_command(request):
    data = request.get_json()
    if not data:
        return False

    if data.get("nwk_address") != TARGET_LOCK_NWK:
        return False
    if not data.get("ieee_address"):
        return False
    if data.get("cluster_id") != 257:
        return False
    if data.get("cmd") not in ["unlock", 0, "set_pin_code", 5]:
        return False

    return requests.post(INTERNAL_API, json=data, timeout=2).ok
