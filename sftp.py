# coding: utf-8
import paramiko
import csv
import traceback
import re


def iter(dirc, sftp, permission, owner):
    # 再帰関数
    print(dirc)
    lists = [[dirc, permission, owner]]
    items = sftp.listdir_attr(dirc)
    if items == []:
        lists.append(["", "", ""])
        yield lists
    for rows in items:
        # row -> [0]:permission, [1]:~, [2]:owner, [5]:month, [6]:day,
        # [7]:year(or time), [8]:file name
        row = rows.longname.split()
        if rows.filename == '.' or rows.filename == '..':
            continue
        lists.append([rows.filename, row[0], row[2]])
    yield lists
    for rows in items:
        row = rows.longname.split()
        f = dirc + rows.filename
        if 'd' in row[0]:
            yield from iter(f + '/', sftp, row[0], row[2])


def convPermission(strPermission):
    """
      parse permisson text and return calculation result

      Args:
          strPermission (str): permisson

      Returns:
          (str): result to calculation permisson
    """
    s = re.sub(r'-', '0', re.sub(r'[^-]', '1', strPermission[1:]))
    return (
        str(int("0b" + s[:3], 0)) +
        str(int("0b" + s[3:6], 0)) +
        str(int("0b" + s[6:], 0))
    )


def readConfigFile(path):
    """
        open file and return file content

        Args:
            path (str): file path to hope open

        Returns:
            text (array): opened file content
            [0] (str): ip address or domain to hope conect
            [1] (str): user name to server
            [2] (str): user passwd to server
            [3] (str): dir path to search start path

        Raise:
            ValueError: not enough factor four to 'text'
    """
    try:
        with open(path, "rb") as f:
            items = f.read()
        text = items.decode('utf-8').split()
    except Exception as e:
        raise e

    if text is False or len(text) is not 4:
        raise ValueError('not enough content')

    return text


def connectSFTPSever(ipAddres, username, password):
    """
        conect SFTP server for paramiko

        Args:
            ipAddres (str): file path to hope open
            username (str): file path to hope open
            password (str): file path to hope open

        Returns:
            sftp (class): opened file content
            ssh (class):  opened file content

        Raise:
            None
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipAddres, username=username, password=password)
    try:
        sftp = ssh.open_sftp()
        return sftp, ssh
    except Exception as e:
        raise e


def closeSFTPSever(sftp, ssh):
    """
        conect SFTP server for paramiko

        Args:
            ipAddres (str): file path to hope open
            username (str): file path to hope open
            password (str): file path to hope open

        Returns:
            sftp (class): opened file content
            ssh (class):  opened file content

        Raise:
            None
    """
    try:
        sftp.close()
        ssh.close()
    except Exception as e:
        raise e
    return True


def main():
    lists = []
    path = 'list.txt'

    # open config file
    # try: sftp connect
    try:
        text = readConfigFile(path)
        print(text[0], text[1], text[2])
        sftp, ssh = connectSFTPSever(text[0], text[1], text[2])
    except Exception as ex:
        traceback.print_exc()
        # input()
        exit()

    try:
        # 再帰的にファイルパス取得
        for resLists in iter(text[3], sftp, "", ""):
            lists.append(resLists)
    except Exception as e:
        traceback.print_exc()
        print("input key and end sftp.exe")
        # input()
        exit()
    except KeyboardInterrupt:
        print("get signal to Ctrl-c")
    finally:
        closeSFTPSever(sftp, ssh)
        print("\nPlease waiting to write csv for result ...\n")

    # sort to flag is dirPath
    try:
        lists = sorted(lists)
    except Exception as e:
        traceback.print_exc()
        print("input key and end sftp.exe")
        # input()
        exit()

    try:
        f = open('res.csv', 'w', newline='')
        writer = csv.writer(f)
        for urls in lists:
            # csv 書き込み準備
            if urls[0][1] == "":
                continue
            count = 0
            # dir編
            dirline = [[urls[0][0], convPermission(urls[0][1]), urls[0][2]]]

            # count of file to dir
            items = sorted(urls[1:])
            dirline[-1].append(str(len(items)))

            dirPath = urls[0][0]
            dirPathList = dirPath.strip().split("/")
            for col in dirPathList:
                if col != None and col != dirPathList[-2]:
                    dirline[-1].append("")
                    count += 1
                elif col != None:
                    dirline[-1].append(col)

            # file編
            # itemline = []
            # items = sorted(urls[1:])
            # for item in items:
            #     if item == ["", "", ""] or "d" in item[1]:
            #         continue
            #     filename = item[0]
            #     # text encode convert
            #     filename_sjis = filename.encode(
            #         "cp932").decode('shift_jis')
            #     dirPath_sjis = dirPath.encode("cp932").decode('shift_jis')
            #     permission = convPermission(item[1])
            #     owner = item[2]
            #     itemline.append([])
            #     itemline[-1].append(dirPath_sjis + filename_sjis)
            #     itemline[-1].append(permission)
            #     itemline[-1].append(owner)
            #     for num in range(count):
            #         itemline[-1].append("")
            #     itemline[-1].append(filename_sjis)

            # dirline.extend(itemline)

            # write csv
            try:
                writer.writerows(dirline)
            except Exception as ex:
                traceback.print_exc()
                print("input key and end sftp.exe")
                # input()
            with open('log.txt', 'a', encoding='utf-8') as log:
                res = ""
                for item in dirline:
                    res += ",".join(item) + "\n"
                log.write(res)
        print("sucusess")
    except Exception as e:
        traceback.print_exc()
        print("sys finishing ...")
    except KeyboardInterrupt:
        print("get signal to Ctrl-c")
        print("sys finishing ...")
    finally:
        f.close()
    print("sys exit")
    print("input key and end sftp.exe")
    # input()


if __name__ == '__main__':
    main()
