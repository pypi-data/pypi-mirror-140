"Script for logging encryption/decryptions, login/logout dates, and password changes for the Revenant app."

import os
from platform import system as get_platform


class UnknownFilesystem(Exception):
        "Raised when the file system is not Linux."
        pass


class Log:
    """
    A logging class.
    """


    def __init__(self, username) -> None:
        self.username = username


    def log_exists(self) -> bool:
        "Checks if a log file exists. Returns a boolean  value."
        if get_platform == "Linux":
            file_name_validity = os.path.exists("/home/{}/.log.log".format(self.username))
            return file_name_validity
        else:
            raise UnknownFilesystem("Unknown filesystem detected; cannot ascertain file existence.")


    def create_log(self) -> int:
        "Creates a log file."
        if get_platform == "Linux":
            with open ("/home/{}/.log.log".format(self.username), "w+") as file:
                file.write("log file created.")
            return 0
        else:
            raise UnknownFilesystem("Unknown filesystem detected; cannot create file.")
        

    def audit(self, keywords:list) -> int:
        if get_platform == "Linux":
            with open ("/home/{}/log.log".format(self.username), "w+") as file:
                lines = file.readlines()
                for word in keywords:
                    for line in lines:
                        if word not in line:
                            file.write(line)
            return 0
        else:
            raise UnknownFilesystem("Unknown filesystem detected; cannot access file.")


    def log(self, logstring:str) -> int:
        if get_platform == "Linux":
            with open ("/home/{}/.log.log".format(self.username), "w") as file:
               file.write("{}\n".format(logstring))
            return 0
        else:
            raise UnknownFilesystem("Unknown filesystem detected; cannot access file")
    

    def change_user(self, new_user:str) -> int:
        self.username = new_user
        return 0