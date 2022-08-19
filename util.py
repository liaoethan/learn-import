import json
import os


def save_as_json(name, object):
    BUILD_DIRECTORY = "build"
    if not os.path.isdir(BUILD_DIRECTORY):
        os.mkdir(BUILD_DIRECTORY)
    with open(f"{BUILD_DIRECTORY}/{name}.json", "w") as outfile:
        outfile.write(json.dumps(object, indent=4))
