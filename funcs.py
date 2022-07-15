import cfscrape
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import parse_qs
import os.path
import pathlib
import logging

logging.basicConfig(filename='log', level=logging.INFO)


def GetViewkeyUrls(url):
    logging.info("Get view key url from: %s", url)
    scraper = cfscrape.create_scraper()
    all_href = []

    try:
        root_html = scraper.get(url).content.decode('UTF-8')
        soup = BeautifulSoup(root_html, 'html.parser')
        for a in soup.find_all('a', href=re.compile(r"viewkey")):
            logging.info("Got view key url: %s", a['href'])
            all_href.append(a['href'])
        return all_href
    except:
        return all_href


def GetBaseUrl(url):
    logging.info("Get base url from: %s", url)
    sep = "&page="
    head, _, _ = url.partition(sep)
    logging.info("Got base url without page num: %s", head)
    base_url = head + sep
    logging.info("Got base url with page num: %s", base_url)
    return base_url


def GetMaxPageNum(url):
    base_url = "https://91porn.com/v.php"
    logging.info("GetMaxPageNum of url: %s", url)
    scraper = cfscrape.create_scraper()
    url = scraper.get(url).content.decode('UTF-8')
    soup = BeautifulSoup(url, 'html.parser')
    div_pagingnav = soup.find_all("div", attrs={"class": "pagingnav"})
    max_page_num = 0
    if len(div_pagingnav) > 0:
        div = div_pagingnav[0]
        not_last_page = div.find_all("a", string="»")
        if len(not_last_page) > 0:
            for div_a in div.find_all("a"):
                logging.info("Got div_a: %s ", div_a)
            curr_max_page = base_url + div.find_all("a")[-2]['href']
            logging.info("curr_max_page: %s", curr_max_page)
            return GetMaxPageNum(curr_max_page)
        else:
            max_page_num = int(
                div.find("span", attrs={"class": "pagingnav"}).string)
            logging.info("max_page_num: %s", max_page_num)
            return max_page_num
    return max_page_num


def GetVid(url):
    logging.info("Getting vid from url: %s", url)
    scraper = cfscrape.create_scraper()
    vid = "0"
    try:
        sub_html = scraper.get(url).content.decode('UTF-8')
        pattern_vid_kv = re.compile(r'VID=\d{3,}')
        vid_kv = re.search(pattern_vid_kv, sub_html)
        if vid_kv:
            _, _, vid = vid_kv.group(0).partition("VID=")
            logging.info("Got vid: %s", vid)
            return vid
        return vid
    except:
        return vid


def Download(vid):
    if vid == "0":
        return
    logging.info("Download from vid: %s ", vid)
    scraper = cfscrape.create_scraper()
    base_path = pathlib.Path(__file__).parent.resolve()
    base_url = "https://cdn77.91p49.com/m3u8/"
    output_path = str(base_path) + "/merged/" + vid + ".mp4"
    logging.info("Download to file: %s ", output_path)

    if os.path.isfile(output_path):
        logging.info("Output file %s exists", output_path)
        return
    else:
        part_num = 1
        while part_num > 0:
            part_url = base_url + vid + "/" + vid + str(part_num) + ".ts"
            logging.info("Downloading %s", part_url)
            try:
                part_res = scraper.get(part_url)
                if part_res.status_code == 200:
                    with open(output_path, "ab") as f:
                        f.write(part_res.content)
                        part_num = part_num + 1
                else:
                    logging.info("Download from vid %s done ", vid)
                    break
            except:
                logging.warning(
                    "Download from vid %s , part_num %s failed", vid, part_num)
                if os.path.isfile(output_path):
                    os.remove(output_path)
                    logging.info("Output file %s deleted", output_path)
                return


def SingleDownload(url):
    logging.info("Download form single url: %s", url)
    vid = GetVid(url)
    Download(vid)


def MultipleDownload(url):
    logging.info("Download from multiple url: %s", url)
    max_page_num = GetMaxPageNum(url)
    logging.info("Got max_page_num: %d", max_page_num)
    base_url = GetBaseUrl(url)
    if max_page_num > 3:
        max_page_num = 3
    for page_num in range(1, max_page_num):
        logging.info("Current page num: %d,  max_page_num: %d",
                     page_num, max_page_num)
        full_url = base_url + str(page_num)
        logging.info("Got full_url %s", full_url)
        view_key_urls = GetViewkeyUrls(full_url)
        for view_key_url in view_key_urls:
            vid = GetVid(view_key_url)
            Download(vid)
