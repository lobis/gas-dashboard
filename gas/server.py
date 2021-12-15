from bs4 import BeautifulSoup
import requests
import os

from pathlib import Path

gas_files_dir = Path.joinpath(Path(__file__).parent.parent, "files/gas")


def get_gas_files():
    gas_files = []
    for gas_file in os.listdir(gas_files_dir):
        if gas_file.split(".")[-1] == "gas":
            gas_files.append(os.path.join(gas_files_dir, gas_file))
    return gas_files


def get_gas_file_urls():
    gas_server_url = "http://sultan.unizar.es/gasFiles"
    page = requests.get(gas_server_url).text
    soup = BeautifulSoup(page, "html.parser")
    return [gas_server_url + "/" + node.get("href") for node in soup.find_all("a") if node.get("href").endswith("gas")]


if __name__ == "__main__":

    contents = set()
    for url in get_gas_file_urls():
        r = requests.get(url)
        content = r.content
        if content in contents:
            print(f"file: {url} content is repeated")
            raise Exception("Gas server has repeated files. Please fix this!")
        contents.add(content)

        filename = os.path.join(gas_files_dir, url.split("/")[-1])
        with open(filename, "wb") as file:
            print(f"Writing gas file to '{filename}'")
            file.write(content)
