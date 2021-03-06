import requests
import json
import shutil
import tarfile
import os
import sys
from pathlib import Path

""" Provide basic colored console print functions
Available types:
*  `print_err` --> prints 'message' with a red color.
*  `warning` --> prints 'message' with a yellow color.
*  `success` -- > prints 'message' with a green color.

All of these bright up 'title' text if provided.
"""


class Colors:
    class Intensives:
        Red = 9
        Green = 10
        Yellow = 11
        Blue = 12
        Pink = 13
        Cyan = 14

    class Standards:
        Red = 1
        Green = 2
        Yellow = 3
        Blue = 4
        Pink = 5
        Cyan = 6

    def print_err(self, error):
        self.__print_colored__(foreground_color=self.Intensives.Red, title="Error", message=error)

    def panic(self, error):
        self.print_err(error)
        exit(0)

    def warning(self, message):
        self.__print_colored__(foreground_color=self.Intensives.Yellow, message=message)

    def success(self, message):
        self.__print_colored__(foreground_color=self.Intensives.Green, message=message)

    @staticmethod
    def __print_colored__(foreground_color, message, title=""):
        if len(title) > 0:
            print("\033[1;38;5;{}m{}: \033[0;38;5;{}m{}\033[0;0;0m".format(foreground_color, title, foreground_color,
                                                                           message))
        else:
            print("\033[0;38;5;{}m{}\033[0;0;0m".format(foreground_color, message))


colors = Colors()


# Downloads from `url`, save it in `filename`, and return written file instance
# Also print download progress


def __download__(url, filename):
    with open(filename, 'wb') as out_file:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')

        columns = int(os.popen('stty size', 'r').read().split()[1]) - 7

        if total is None:
            out_file.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            for d in response.iter_content(chunk_size=128):
                downloaded += len(d)
                out_file.write(d)
                percent = int(downloaded / total * 100)
                done = int(columns * downloaded / total)
                sys.stdout.write('\r[{}{}] %{}'.format('█' * done, '.' * (columns - done), percent))
                sys.stdout.flush()
    sys.stdout.write('\n')
    return out_file


def __newer_version_exists(local, remote):
    remote = [int(x) for x in str(remote).split(".")]
    local = [int(x) for x in str(local).split(".")]
    for i in range(3):
        if local[i] < remote[i]:
            return True
    return False


def __update__():
    # existence of `package.json` file
    if not Path("package.json").is_file():
        colors.panic(error="Not found 'package.json'.")

    # loading `package.json`
    with open("package.json") as f:
        package = json.load(f)

    # checking existence and validation of `swagger-ui` key value
    if "swagger-ui" not in package:
        colors.print_err("Not found 'swagger-ui' in 'package.json'.")
        package["swagger-ui"] = "0.0.0"
    elif str(package["swagger-ui"]).startswith("v") or len(str(package["swagger-ui"]).split(".")) != 3 or False in [
         x.isdigit() for x in str(package["swagger-ui"]).split(".")]:
        colors.print_err("Invalid 'swagger-ui' value found in 'package.json' ({}).".format(package["swagger-ui"]))
        package["swagger-ui"] = "0.0.0"

    # existence and fix `api-doc` path
    if "api-doc" in package:
        destination = str(package["api-doc"])
        if destination.endswith("/"):
            destination = destination[:-1]
    else:
        destination = "public/api-doc"

    # make parent directories for `api-doc` provided path if not exist
    if not Path(destination).is_dir():
        Path(destination).mkdir(parents=True, exist_ok=True)

    # issue a request to get `swagger-ui` latest release
    res = requests.get("https://api.github.com/repos/swagger-api/swagger-ui/releases/latest")

    # checking response
    if not res.ok:
        colors.panic("Error occurred in getting Swagger UI releases info.")

    # converting `bytes` type response to Python `dict`
    data = json.loads(res.text)

    # checking whether response has required fields
    if "tag_name" not in data or "tarball_url" not in data:
        colors.panic("Invalid response received from Github.")

    """
    Check for latest release version
    if update is available:
      1. download tarball package
      2. extract it
      3. move `dist` directory contents to `api-doc` provided path
      4. remove both archive package and unnecessary extracted files  
    """
    if __newer_version_exists(local=package["swagger-ui"], remote=data["tag_name"][1:]):
        colors.warning("Newer release found ({})".format(data["tag_name"]))
        colors.warning("Downloading tar package... ({})".format(data["tarball_url"]))

        extract_dir = "swagger-ui-" + data["tag_name"]
        # downloading
        downloaded_file = __download__(data["tarball_url"], extract_dir + ".tar.gz")
        colors.warning("Extracting package into '{}'...".format(destination))

        # extracting
        tar = tarfile.open(downloaded_file.name, "r:gz")
        tar.extractall(extract_dir)
        tar.close()

        # finding Github-added base directory name
        dir_name = next(os.walk(extract_dir))[1][0]
        src = extract_dir + "/" + dir_name + "/dist/"
        files = os.listdir(src)

        # moving `dist` directory contents (overwrite if exists)
        for f in files:
            shutil.move(os.path.join(src, f), os.path.join(destination, f))

        colors.success("Extracted into '{}'.".format(destination))

        # cleaning up
        shutil.rmtree(extract_dir, ignore_errors=True)
        os.remove(extract_dir + ".tar.gz")
        colors.success("Cleaned up!")

        # updating `package.json`
        package["swagger-ui"] = data["tag_name"][1:]
        with open("package.json", "w") as p:
            json.dump(package, p, indent=2)
        colors.success("'package.json' updated.")

    else:
        colors.success(
            "No updates found for package `swagger-ui`. Current: {} - Latest: {}".format(package["swagger-ui"],
                                                                                         data["tag_name"][1:]))


if __name__ == "__main__":
    __update__()
