# coding: utf-8
import paramiko
import csv
import traceback
import re

# import time
import stat


def iter(dirc, sftp, permission, owner):
    # 再帰関数
    print(dirc)
    lists = [[dirc, permission, owner]]
    items = sftp.listdir_attr(dirc)

    if items == []:
        lists.append(['', '', ''])
        yield lists

    for rows in items:
        # 名前
        name = joinVoicedSound(rows.filename).encode(
            'cp932').decode('shift_jis')
        # ファイルパス
        filePath = dirc + name
        # ユーザーID
        owner = str(rows.st_uid)
        # 権限
        permission = stat.filemode(rows.st_mode)
        # 作成時間 time型
        # time = time.gmtime(rows.st_mtime)

        if name == '.' or name == '..':
            continue

        if 'd' in permission:
            yield from iter(filePath + '/', sftp, permission, owner)

        lists.append([name, permission, owner])

    yield lists


def joinVoicedSound(text='') -> str:
    if text == '':
        return ''

    repdict = dict()
    for tap in [(chr(ord(c)) + '\u3099', chr(ord(c) + 1)) for c in u'かきくけこさしすせそたちつてとはひふへほカキクケコサシスセソタチツテトハヒフヘホ']:
        repdict.update({tap[0]: tap[1]})
    for key in repdict.keys():
        text = text.replace(key, repdict.get(key))

    return text


def convPermission(strPermission: str) -> str:
    """
      parse permisson text and return calculation result

      Args:
          strPermission (str): permisson

      Returns:
          (str): result to calculation permisson
    """
    s = re.sub(r'-', '0', re.sub(r'[^-]', '1', strPermission[1:]))
    return (
        str(int('0b' + s[:3], 0)) +
        str(int('0b' + s[3:6], 0)) +
        str(int('0b' + s[6:], 0))
    )


def readConfigFile(path: str) -> list:
    """
        open file and return file content

        Args:
            path (str): file path to hope open

        Returns:
            text (array): opened file content
            [0] (str): ip-address or domain-name to conect
            [1] (str): user name to server
            [2] (str): user passwd to server
            [3] (str): dirctry-path to search start

        Raise:
            ValueError: not enough factor four to 'text'
    """
    try:
        with open(path, 'rb') as f:
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
    path = './list.txt'

    # open config file
    # try: sftp connect
    try:
        text = readConfigFile(path)
    except Exception:
        traceback.print_exc()
        exit()

    try:
        domain = text[0]
        user = text[1]
        passwd = text[2]
        startPath = text[3]
        print(domain, user, passwd)
    except Exception:
        pass

    try:
        sftp, ssh = connectSFTPSever(domain, user, passwd)
    except Exception:
        traceback.print_exc()
        exit()

    try:
        # 再帰的にファイルパス取得
        for resLists in iter(startPath, sftp, '', ''):
            lists.append(resLists)
    except Exception:
        traceback.print_exc()
        print('input key and end sftp.exe')
        exit()
    except KeyboardInterrupt:
        # pythonでの実行時のみ動作確認
        # pyinstallerでexe化した場合は動作せず
        print('get signal to Ctrl-c')
    finally:
        closeSFTPSever(sftp, ssh)
        print('\nPlease waiting to write csv for result ...\n')

    # sort to flag is dirPath
    try:
        lists = sorted(lists)
    except Exception:
        traceback.print_exc()
        print('input key and end sftp.exe')
        exit()

    try:
        f = open('res.csv', 'w', newline='')
        writer = csv.writer(f)

        # 初期ディレクトリを記載
        dirList = startPath.strip().split('/')
        dirline = ['', '', '']
        dirline.extend(dirList)
        writer.writerows([dirline])

        for urls in lists:
            # csv 書き込み準備
            if urls[0][1] == '':
                continue
            count = 0
            # dir編
            dirline = [[urls[0][0], convPermission(urls[0][1]), urls[0][2]]]
            dirPath = urls[0][0]
            dirPathList = dirPath.strip().split('/')
            for col in dirPathList:
                if col is not None and col != dirPathList[-2]:
                    dirline[-1].append('')
                    count += 1
                elif col is not None:
                    dirline[-1].append(col)

            # file編
            itemline = []
            items = sorted(urls[1:])
            for item in items:
                if item == ['', '', ''] or 'd' in item[1]:
                    continue
                filename = item[0]
                permission = convPermission(item[1])
                owner = item[2]
                itemline.append([])
                itemline[-1].append(dirPath + filename)
                itemline[-1].append(permission)
                itemline[-1].append(owner)
                for num in range(count):
                    itemline[-1].append('')
                itemline[-1].append(filename)

            # ここをコメントアウトでディレクトリ一覧出力に切り替え
            dirline.extend(itemline)

            # write csv
            try:
                writer.writerows(dirline)
            except Exception:
                traceback.print_exc()
                print('input key and end sftp.exe')

            with open('log.txt', 'a', encoding='utf-8') as log:
                res = ''
                for item in dirline:
                    res += ','.join(item) + '\n'
                log.write(res)

        print('sucusess')
    except Exception:
        traceback.print_exc()
        print('sys finishing ...')
    except KeyboardInterrupt:
        print('get signal to Ctrl-c')
        print('sys finishing ...')
    finally:
        f.close()

    print('sys exit')
    print('input key and end sftp.exe')


if __name__ == '__main__':
    main()
