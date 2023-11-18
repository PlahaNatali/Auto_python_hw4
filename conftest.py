import random
import string
from datetime import datetime
import pytest
import yaml
from checkers import ssh_checkout, ssh_getout, ssh_wpapper
from files import upload_files

with open('config.yaml') as f:
    # читаем документ YAML
    data = yaml.safe_load(f)


@pytest.fixture()  # создает директории
def make_folders():
    return ssh_checkout("mkdir -p {} {} {} {}".format(data["folder_in"], data["folder_out"], data["folder_ext"],
                                                      data["folder_ext2"]), "")


@pytest.fixture(autouse=True, scope="module")  # затем очищает эти директории
def clear_folders():
    return ssh_checkout("rm -rf {}/* {}/* {}/* {}/*".format(data["folder_in"], data["folder_in"], data["folder_ext"],
                                                            data["folder_ext2"]), "")


@pytest.fixture(autouse=True, scope="module")  # после создает файлы
def make_files():
    list_of_files = []
    for i in range(data["count"]):
        filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if ssh_checkout("cd {}; dd if=/dev/urandom of={} bs={} count=1 iflag=fullblock".format(data["folder_in"],
                                                                                               filename, data["bs"]),
                        ""):
            list_of_files.append(filename)
    return list_of_files


@pytest.fixture()
def make_subfolder():
    testfilename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    subfoldername = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    if not ssh_checkout("cd {}; mkdir {}".format(data["folder_in"], subfoldername), ""):
        return None, None
    if not ssh_checkout("cd {}/{}; dd if=/dev/urandom of={} bs=1M count=1 iflag=fullblock".format(data["folder_in"],
                                                                                                  subfoldername,
                                                                                                  testfilename), ""):
        return subfoldername, None
    else:
        return subfoldername, testfilename


@pytest.fixture()
def make_bad_arx():
    ssh_checkout("cd {}; 7z a {}/bad_arx".format(data["folder_in"], data["folder_out"]), "Everything is Ok")
    ssh_checkout("truncate -s 1 {}/bad_arx.7z".format(data["folder_out"]), "")


@pytest.fixture(autouse=True, scope="module")
def deploy():
    res = []
    upload_files("/home/user/p7zip-full.deb",
                 "/home/user2/p7zip-full.deb")
    res.append(ssh_checkout("echo '2222' | sudo -S dpkg -i /home/user2/p7zip-full.deb",
                            "Настраивается пакет"))
    res.append(ssh_checkout("echo '2222' | sudo -S dpkg -s p7zip-full",
                            "Status: install ok installed"))
    return all(res)


def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture(autouse=True)
def write_stat():
    yield
    proc_loadavg = ssh_getout("cat /proc/loadavg")
    time = get_time()
    with open(data["stat_file"], "a+") as file:
        file.write(f'time: {time}; count: {data["count"]}; bs: {data["bs"]}; proc_loadavg: {proc_loadavg}')


@pytest.fixture(autouse=True)
def safe_log():
    start_time = get_time()
    yield
    with open(data["log_file"], 'a+') as f:
        f.write(ssh_getout("journalctl --since {}".format(start_time)))