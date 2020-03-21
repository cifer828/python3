#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Replace image of oli markdown doc with local image
author: Cifer Z.
date: 3/13/20
"""

import os
import urllib.request
import re


def get_markdown_path(root):
    """
    :param root: root directory of all markdown
    :return list of path
    """
    md_list = []
    for (dirname, dirs, files) in os.walk(root):
        # recurse all files in root directory
        for filename in files:
            # traverse all files in one folder
            if filename.endswith('.md'):
                md_list.append(os.path.join(dirname, filename))
    return md_list


def replace_image(md_path):
    """
    1. download image in markdown to "image" file and replace link with local images
    2. replace global image link to local image link
    :param md_path: path of markdown file
    """
    print("\nProcessing {}: {} ...".format(md_path.split("/")[-2], md_path.split("/")[-1]))

    with open(md_path, "r") as f:
        markdown = f.read()

    # download and replace image from internet
    image_link_pattern = re.compile("http[^)]+(?:png|jpg)")
    image_links = re.findall(image_link_pattern, markdown)
    dir_path = os.path.dirname(md_path)
    for link in image_links:
        # print(link)
        image_name = link.split("/")[-1]
        markdown = markdown.replace(link, "image/" + image_name)
        if "youtube" not in link:
            urllib.request.urlretrieve(link, os.path.join(dir_path, "image", image_name))
    print("Downloaded {} images".format(len(image_links)))

    # replace global image with local image
    global_image_pattern = re.compile("/Users/[^)]+[png|jpg]")
    image_links = re.findall(global_image_pattern, markdown)
    for link in image_links:
        markdown = markdown.replace(link, "image/" + link.split("/")[-1])
    print("Replaced {} local image paths".format(len(image_links)))

    with open(md_path, "w") as f:
        f.write(markdown)


if __name__ == "__main__":
    root = "/Users/qiuchenzhang/Documents/CMU/Notes/15619-oli"
    paths = get_markdown_path(root)
    for path in paths:
        replace_image(path)


