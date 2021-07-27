from suricatasc import SuricataSC


class Suricata_Dataset:
    def __init__(self, path_socket="/var/run/suricata/suricata-command.socket"):
        self.sc = SuricataSC(path_socket, verbose=True)

    def add_dataset(self, name: str, type_data: str, value: str) -> bool:
        """Add a indicator of the dataset of Suricata.

        Args:
            name (str): [name of the dataset]
            type_data (str): [type of dataset]
            value (str): [value of the indicator]

        Returns:
            [bool]: [result to add indicator]
        """

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

    def remove_dataset(self, name: str, type_data: str, value: str) -> bool:
        """Remove a valut of the dataset of Suricata .

        Args:
            name (str): [description]
            type_data (str): [description]
            value (str): [description]

        Returns:
            bool: [description]
        """
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
        """Connects to the UNIX socket."""
        self.sc.connect()

    def disconnect(self):
        """Disconnects from the UNIX socket ."""
        self.sc.close()
