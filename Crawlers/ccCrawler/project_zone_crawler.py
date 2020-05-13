#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Save project writeup of CMU 15619
website: https://theproject.zone/s20-15619

@author: Cifer Z.
@date: 3/11/20
"""

import requests
import os
import urllib.request
import shutil
from bs4 import BeautifulSoup


def parse_cookie(cookie_str: str):
    """
    Convert cookie string to cookie dict
    :param cookie_str: cookie string
    :return: cookie dict
    """
    cookie_list = [pair.strip().split("=") for pair in cookie_str.split(";")]
    cookie_dict = dict(cookie_list)
    return cookie_dict


class WriteupCrawler:
    def __init__(self, root_dir, cookie_str):
        """
        Constructor
        :param cookie_str: cookie string pasted from browser
        """
        self.root_dir = root_dir
        self.cookies = parse_cookie(cookie_str)
        self.base_url = "https://theproject.zone/s20-15619/"
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Host": "theproject.zone",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:72.0) Gecko/20100101 Firefox/72.0",
            "Referer": "https://theproject.zone/login/?next=/s20-15619"
        }
        self.index_html = ""

    def download_projects(self, overwrite=False):
        """
        Parse the index page and download each project if it is unlocked
        :param overwrite: overwrite old files or not
        """
        re = requests.get(self.base_url, headers=self.headers, cookies=self.cookies)
        index_html = re.content.decode("utf8")
        soup = BeautifulSoup(index_html, "html5lib")
        panels = soup.select("body > div > div > div > div > div > div.panel-body > div.panel-default")

        # create root directory or remove it if exists then create a new one
        if overwrite and os.path.exists(self.root_dir):
            print("Cleaning existing files...")
            shutil.rmtree(self.root_dir)
        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)

        # traverse project group
        for panel in panels:
            project_group = panel.select("div.panel-heading > h3")[0].contents[2].strip().replace(" ", "")
            row = panel.select("tbody > tr")

            # traverse each project
            for tr in row:
                td = tr.select("td")[0]
                unlocked = td.a

                # download project writeup if it is unlocked
                if unlocked:
                    project_url = td.find("a")["href"].split("/")[-1]
                    # remove / from project name
                    project_name = td.find("a").get_text().strip().replace("/", "").replace(" ", "-")
                    self.download_single_project(self.base_url + project_url, project_group,  project_name)
                    td.find("a")["href"] = os.path.join(os.path.join(project_group, project_name, project_name + ".html"))
                else:
                    project_name = td.get_text().strip().replace(" ", "-")
                    print("\n" + project_group + ": " + project_name + "is locked")

        # remove account email
        soup.select("#navbar > ul > li > button")[0].extract()
        # save index html file
        index_path = os.path.join(self.root_dir, "project_zone.html")
        with open(index_path, "w") as f:
            f.write(str(soup))

    def download_single_project(self, project_url: str, project_group: str, project_name: str, overwrite=False):
        """
        Download html and image of single project page,
        Replace image link with local image
        :param project_group: project group, e.g. Primers, Project0
        :param project_name: project name also the name of directory and html
        :param project_url: url for the project page
        :param overwrite: overwrite old files or not
        """
        # check if file exists for not-overwrite mode
        file_path = os.path.join(self.root_dir, project_group, project_name)
        if not overwrite and os.path.exists(file_path):
            print(file_path + " exists.")
            return
        # parse the page
        print("\nParsing project: {}: {} from {}".format(project_group, project_name, project_url))
        re = requests.get(project_url, headers=self.headers, cookies=self.cookies)
        html = re.content.decode("utf8")
        soup = BeautifulSoup(html, "html5lib")

        # create local directory for this project
        os.makedirs(file_path)

        # download image and replace link on cloud with local link
        img_tag = soup.select("div.container-fluid")[0].find_all("img")
        print("Downloading images...")
        for img in img_tag:
            # remove space in url
            img_src = img['src']
            img_src = img_src.replace(" ", "%20")
            img_name = img_src.split("/")[-1]
            # download img and replace src attribute
            img_path = os.path.join(self.root_dir, project_group, project_name,  img_name)
            urllib.request.urlretrieve(img_src, img_path)
            img['src'] = img_name
            # add bootstrap tag to format image
            # check if img has "class" attribute
            img['class'] = img['class'] + " img-thumbnail " if img.has_attr("class") else "img-thumbnail"

        # format page
        container_div = soup.select("body > div.container.outer.wrapper")[0]
        container_div["class"].append("col-lg-12")
        # fix return link to the index page
        home_page = soup.select("body > div:nth-child(1) > nav > div.navbar-header > span > a")[0]
        home_page["href"] = "../../project_zone.html"
        # remove account email
        soup.select("#navbar > ul > li > button")[0].extract()
        # save html
        html_path = os.path.join(self.root_dir, project_group, project_name, project_name + ".html")

        with open(html_path, "w") as f:
            f.write(str(soup))

        print("Successfully saved project: " + project_name)


if __name__ == "__main__":
    # 1. login to https://theproject.zone/s20-15619
    # 2. open more tools > developer tools
    # 3. open network tab, reload page
    # 4. find the a html file named "s20-15619"
    # 5. copy cookie string from request header
    # 6. specify local dir to download files
    cookie_string = "_ga=GA1.2.1613336051.1578938483; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1; _gid=GA1.2.747882950.1587617528; csrftoken=oMqDSNOiqRYcEzb3Usj9uJjPkQuD2gtKNeJqn2CtG8NXT1Kf58Mwr9OmJmGWIyaA; sessionid=l1lbtk4s7qixecv6qukfcvq7ugb7sio7; _gat=1"
    root = "/Users/qiuchenzhang/Documents/CMU/2020 Spring/15619 Cloud Computing/15619-writeup/"

    crawler = WriteupCrawler(root, cookie_string)
    crawler.download_projects()

    # crawler.download_single_project("https://theproject.zone/s20-15619/account-setup",
    #                                 "Primers",
    #                                 "Cloud account setup (Required)".replace(" ", "-"))
