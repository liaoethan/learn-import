import configuration
import json
import logging
import logging.config
import mimetypes
import os
import time
import oauth_token
import requests

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)

config = configuration.get_config()

logger.info(
    "Using host "
    + config["OAUTH_HOST"]
    + " and site "
    + config["SITE_ID"]
    + " and structureId "
    + str(config["ARTICLE_STRUCTURE_ID"])
)

REPOSITORY_ID = 83630
FOLDER_ID = 268532

session = requests.Session()
authorization = oauth_token.get_oauth_token(config)
headers = {
    "Accept": "application/json",
    "Authorization": authorization,
    "Content-Type": "application/json",
}
uri = f"{config['OAUTH_HOST']}/api/jsonws/invoke"
method = "POST"


def get_byte_array_string(filepath):
    start = time.perf_counter()
    f = open(
        filepath,
        "rb",
    )
    byteArrayContents = bytearray(f.read())
    bytes = "["
    for integer in byteArrayContents:
        bytes += str(integer) + ","
    bytes = bytes.rstrip(",")
    bytes += "]"
    end = time.perf_counter()
    print(f"Read file in {end - start:0.4f} seconds.")
    return bytes


def load_files(filepaths):

    cmd = []
    for filepath in filepaths:
        image_type = mimetypes.guess_type(filepath)
        mime_type = image_type[0]
        if mime_type is None:
            raise Exception("cannot figure out mimetype for" + filepath)

        filename = os.path.basename(filepath)
        cmd.append(
            {
                "/dlapp/add-file-entry": {
                    "externalReferenceCode": filename,
                    "repositoryId": REPOSITORY_ID,
                    "folderId": FOLDER_ID,
                    "sourceFileName": filename,
                    "mimeType": mime_type,
                    "title": filename,
                    "urlTitle": filename,
                    "description": "",
                    "changeLog": "1.0",
                    "bytes": get_byte_array_string(filepath),
                    "expirationDate": 0,
                    "reviewDate": 0,
                }
            }
        )
    start = time.perf_counter()
    res = session.request(method, uri, headers=headers, data=json.dumps(cmd))
    end = time.perf_counter()
    print(f"api call in {end - start:0.4f} seconds.")
    print(res.status_code)


files = []

for root, d_names, f_names in os.walk(config["SPHINX_OUTPUT_DIRECTORY"] + "/commerce"):
    if root.endswith("_images"):
        for f in f_names:
            filename = str(os.path.join(root, f))
            files.append(filename)

load_files(files)
