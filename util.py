import hashlib
import json
import os


def save_as_json(name, object):
    BUILD_DIRECTORY = "build"
    if not os.path.isdir(BUILD_DIRECTORY):
        os.mkdir(BUILD_DIRECTORY)
    with open(f"{BUILD_DIRECTORY}/{name}.json", "w") as outfile:
        outfile.write(json.dumps(object, indent=4))


def sha_256sum(filename):
    BLOCK_SIZE = 65536

    file_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(BLOCK_SIZE)

    return file_hash.hexdigest()
