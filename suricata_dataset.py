from suricatasc import SuricataSC


class Suricata_Dataset:
    def __init__(self, path_socket="/var/run/suricata/suricata-command.socket"):
        self.sc = SuricataSC(path_socket, verbose=True)

    def add_dataset(self, name, type_data, value):

        cmd, args = self.sc.parse_command(
            "dataset-add %s %s %s" % (name, type_data, value)
        )
        if cmd and args:
            message = self.sc.send_command(command=cmd, arguments=args)
            if message["return"] == "OK":
                return True
            else:
                return False
        else:
            return False

    def remove_dataset(self, name, type_data, value):
        cmd, args = self.sc.parse_command(
            "dataset-remove %s %s %s" % (name, type_data, value)
        )
        if cmd and args:
            message = self.sc.send_command(command=cmd, arguments=args)
            if message["return"] == "OK":
                return True
            else:
                return False
        else:
            return False

    def connect(self):
        self.sc.connect()

    def disconnect(self):
        self.sc.close()
