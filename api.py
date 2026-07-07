import requests
import envs
import urllib.parse

MEDIA_ENDPOINT = "/api/perchai/media?status=undetected&limit=1000"
POST_DETECTED_MEDIA_ENDPOINT = "/api/perchai/detected_media"


def is_service_alive() -> bool:
    url = urllib.parse.urljoin(envs.PERCH_MOUNT_SYSTEM_HOST, "ping")
    response = requests.get(url)

    return response.status_code == 200


def get_undetected_media() -> list[dict]:
    url = urllib.parse.urljoin(envs.PERCH_MOUNT_SYSTEM_HOST, MEDIA_ENDPOINT)
    response = requests.get(url)
    return response.json()


def upload_detected_media(media: list[dict]):
    url = urllib.parse.urljoin(
        envs.PERCH_MOUNT_SYSTEM_HOST, POST_DETECTED_MEDIA_ENDPOINT
    )
    r = requests.post(url, data=media)
