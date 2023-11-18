import yaml

from checkers import ssh_checkout_negative

with open('config.yaml') as f:
    # читаем документ YAML
    data = yaml.safe_load(f)


class TestNegative:
    def test_step1(self, make_bad_arx):
        assert ssh_checkout_negative("cd {}; 7z e bad_arx.7z -o{} -y".format(data["folder_out"],
                                                                             data["folder_ext"]),
                                     "ERRORS"), "Test1 FAIL"

    def test_step2(self):
        # test2 =========show info about arx2.7z
        assert ssh_checkout_negative("cd {}; 7z t bad_arx.7z".format(data["folder_out"]), "ERRORS"), "Test2 FAIL"