import pathlib
import logging

from funcs import *


def main():
    logging.basicConfig(filename='log', level=logging.INFO)
    base_path = pathlib.Path(__file__).parent.resolve()
    logging.info("base_path: %s", base_path)
    urls_file = str(base_path) + "/urls"
    logging.info("urls_file: %s", urls_file)

    with open(urls_file) as urls_f:
        urls = urls_f.readlines()

    for url in urls:
        url = url.rstrip()
        logging.info("url: %s", url)
        if len(url) == 0:
            continue
        single_pattern = re.compile(r"viewkey")
        if re.search(single_pattern, url):
            SingleDownload(url)
        else:
            MultipleDownload(url)


if __name__ == '__main__':
    main()
