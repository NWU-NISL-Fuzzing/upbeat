import json
import os
import re

total_num = 0


def get_all_folders(path):
    folders = []
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            folders.append(os.path.join(root, dir))
    return folders


def get_all_qsharp_files(path):
    # total_num = 0
    global total_num

    file_list = []
    # tqdm.write("now reading path:"+path)
    for file in os.listdir(path):
        tmp_path = path + "/" + file
        # print("check:"+tmp_path)
        if os.path.isdir(tmp_path):
            file_list.extend(get_all_qsharp_files(tmp_path))
        elif file.endswith('.qs'):
            file_list.append(tmp_path)
            total_num += 1
    # print("here are totally "+str(total_num)+" files.")
    return file_list


def read_text(path):
    """ read text """

    content = ""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        # print("have read:"+str(len(content)))
    return content


def write_text(path, content):
    """ write text """

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    # print("already write")


def add_to_write(path, content):
    """ add to write """

    with open(path, "a+", encoding="utf-8") as f:
        f.write(content)
    # print("already write")


def write_down(path: str, fragment_list: list):
    print("start to write")
    if os.path.exists(path):
        os.remove(path)
    with open(path, "a") as f:
        for fragment in fragment_list:
            f.write(str(fragment) + "\n")


def initParams(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
    data = json.loads(content)
    return data


def delete_comment(content: str) -> str:
    regex = r" *\/\/(.*?)\n"
    matches = re.finditer(regex, content)
    for match in matches:
        content = content.replace(match.group(0), "")
    return content


def delete_existing(path: str):
    if os.path.exists(path):
        os.remove(path)
