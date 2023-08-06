import os
from time import sleep
import PySimpleGUI as sg
from Crypto.Protocol.KDF import PBKDF2
from better_cryptography import Ciphers, Log, compare_hashes, hash_ 
# GOAL FOR TODAY:
# Fix up logic errors and convert keymaking from SHA256 to PBKDF2.
# Fix logging in.


class login:
    """
    Class responsible for logging the user in.
    """
    def __init__(self) -> None:
        pass
    

    def rand_hash(self) -> str:
        "a function to generate random hex-encoded hashes."
        rand_bytes = os.urandom(32)
        rand_hash = hash.sha256(rand_bytes)
        return_value = rand_hash.hexdigest()
        return return_value
    

    def login_sequence(self, password=str, username=str, count=int) -> int:
        """
        Main login sequence. Runs once.
        code of 0: no errors detected.
        Error code of 1: Username is invalid.
        error code of 2: given password did not match cached password.
        error code of 3: password or username was not given.
        """
        # checking if five incorrect attempts to login have occurred.
        if count == 5:
            sg.popup_auto_close("Invalid credentials entered at least 5 times. Exiting application...", font="Helvetica")
            quit()
        # guard clause
        if password == "" or username == "":
            return 3
        # checking if user is valid
        elif os.path.exists("/home/{}/".format(username)) is False:
            return 1
        # accessing the password cache and extracting its contents.
        try:
            with open ("/home/{}/Revenant/.password.hash".format(username), 'r') as file:
                contents = file.read()
        except FileNotFoundError:
            sg.popup_error("Password cache not found. Reinstall with the most recent password and decrypt any encrypted files.\nThis program will now quit.", font='Helvetica')
            quit()
        length = len(contents)
        # getting the hash and salt from cache
        password_hash = contents[0:length:4]; salt = contents[1:length:4]
        # creating the hash object and comparing
        full_object = password + username.strip() + salt; full_hash = hash.sha256(full_object.encode()); hex_digest = full_hash.hexdigest()
        # returning values
        if password_hash == hex_digest:
            return 0
        elif password_hash != hex_digest:
            sleep(5)
            return 2


    def change_password(self, old_password=str, new_password=str, username=str):
        """
        Module for changing password. Can return either an integer or string.
        String returned: There were no error codes.
        Error code of 1: Old password or new password was not supplied.
        Error code of 2: Old password was not correct.
        """
        if old_password == "" or new_password == "":
            return 1
        list_ = []
        # accessing the cache to extract contents
        try:
            with open ("/home/{}/Revenant/.password.hash".format(username), 'r') as file:
                contents = file.read()
        except FileNotFoundError:
            sg.popup_error("Password cache not found. Reinstall with the most recent password and decrypt any encrypted files. This program will now quit.", font='Helvetica')
            quit()
        # getting hash and salt
        length = len(contents); pass_hash = contents[0:length:4]; salt1 = contents[1:length:4]
        # creating hash object and comparing
        full = old_password + username.strip() + salt1; hashed = hash.sha256(full.encode()); hex_string = hashed.hexdigest()
        if hex_string == pass_hash:
            # creating new salt and two filler hash strings
            new_salt = self.rand_hash(); filler_1 = self.rand_hash(); filler_2 = self.rand_hash()
            # creating the new object
            full_object = new_password + username.strip() + new_salt; password_hash = hash.sha256(full_object.encode()); hex_digest = password_hash.hexdigest()
            # layering hash
            for i in range(64):
                # breaking blocks up into 4 character blocks and appending to the list
                single_hash_pass = hex_digest[i]; single_salt = new_salt[i]; filler_1_single = filler_1[i]; filler_2_single = filler_2[i]
                combined_hash_block = single_hash_pass + single_salt + filler_1_single + filler_2_single; list_.append(combined_hash_block)
            # combining hash blocks
            layered_hash = "".join(list_)
            sg.popup_auto_close("Parsing Drive. This may take a while.", font="Helvetica", non_blocking=True)
            # looping through every file 
            old_cipher = Ciphers(old_password)
            new_cipher = Ciphers(new_password)
            for root, dirs, files in os.walk("/home/{}/".format(username)):
                for file in files:
                    path_of_file = os.path.join(root, file)
                    with open(path_of_file, "rb") as file:
                        encryption_type = file.read(3)
                    if encryption_type == b"AES":
                        old_cipher.AES_decrypt_file(path_of_file)
                        new_cipher.AES_encrypt_file(path_of_file)
                    elif encryption_type == b"BLO":
                        old_cipher.BLO_decrypt_file(path_of_file)
                        pass
                    elif encryption_type == b"FER":
                        pass
                    else:
                        continue
            # writing the new password to the cache
            del old_cipher; del new_cipher
            with open("/home/{}/Revenant/.password.hash".format(username), 'w') as file:
                file.write(layered_hash)
            # returning the new password so that the while True: loop doesn't throw a fit. Else, returning 2.
            return new_password
        elif hex_string != pass_hash:
            return 2


# layouts 
sg.theme("DarkBlue")
login_layout = [
    [sg.Text('Enter current Linux username. This will be used to access relevant directories/files.', font="Helvetica")],
    [sg.InputText(key='username', font="Helvetica", border_width=10)],
    [sg.Text("Enter password.", font="Helvetica")],
    [sg.InputText(key="password", password_char='*', font="Helvetica", border_width=10)],
    [sg.Button("Ok", font="Helvetica", border_width=10), sg.Button("Close Window", font="Helvetica", border_width=10)]
] # this layout is done
logged_layout = [
    [sg.Text('Password confirmed, user logged. What would you like to do?', font="Helvetica", border_width=10)],
    [sg.Button('Edit file configurations', key="file_hub", font="Helvetica", border_width=10),
    sg.Button('Change my password', key='password_change', font="Helvetica", border_width=10)],
    [sg.Button('Close Window', key='Close', font="Helvetica", border_width=10)]
] # this layout is done
change_pass_layout = [
    [sg.Text("Please enter your current password.", font="Helvetica")],
    [sg.InputText(key="old_password", password_char='*', font="Helvetica", border_width=10)],
    [sg.Text("Please enter your new password.", font="Helvetica")],
    [sg.InputText(key="new_password", password_char="*", font="Helvetica", border_width=10)],
    [sg.Button("Ok", key="OK_pass", font="Helvetica", border_width=10), sg.Button("Go back", key="back_pass", font="Helvetica", border_width=10)]
] # also done
file_hub_script_layout = [
    [sg.Text("Please select a command.", font="Helvetica")],
    [sg.Frame("External file commands",[
        [sg.Button("File encryption - encrypts a singular file, given the path.", key="file_encrypt", font="Helvetica"),
        sg.Button("File decryption - decrypts an already encrypted file, given the path.", key="file_decrypt", font="Helvetica")]],
        border_width=10, background_color="#626a80", element_justification="C")],
    [sg.Frame('External folder commands',[
        [sg.Button("Folder encryption - encrypts a singular folder, given the path.",key="folder_encrypt", font="Helvetica"),
        sg.Button("Folder decryption - decrypts an already encrypted folder, given the path.", key='folder_decrypt', font="Helvetica")]],
        border_width=10, background_color="#626a80", element_justification="C")],
    [sg.Frame('Vault commands',[
        [sg.Button("Encrypt Vault - encrypts every non-encrypted file in the Vault folder.", key="vault_encrypt", font="Helvetica"),
        sg.Button('Decrypt Vault - decrypts every encrypted file in the Vault folder.', key="vault_decrypt", font="Helvetica")]],
        border_width=10, background_color="#626a80", element_justification="C")],
    [sg.Button('Back - Go back to previous screen', key='back', font="Helvetica", border_width=10), sg.Button("Audit UserLog File", key="Intiate_audit", font="Helvetica", border_width=10)],
    [sg.Button("Logout - terminates application and logs user out.", key="logout", font="Helvetica", border_width=10)]
]# this layout is done
userLog_audit_layout = [
    [sg.Text("UserLog Audit Mode selected. What would you like to do?")],
    [sg.Button("Remove singular file Encryption/Decryption logs", key="single_file_log_audit", font="Helvetica", border_width=10),
    sg.Button("Remove Folder Encryption/Decryption Logs", key="folder_logs_audit", font="Helvetica", border_width=10)],
    [sg.Button("Remove Vault Encryption/Decryption Logs", key="vault_log_audit", font="Helvetica", border_width=10),
    sg.Button('Clear userlog.', key="Clear_userlog", font="Helvetica", border_width=10)],
    [sg.Button("Return to previous screen", key="audit_return", font="Helvetica", border_width=10),
    sg.Button("Close Window", key="Close_Audit", font="Helvetica", border_width=10)]
]
layout = [
    [sg.Column(login_layout, key="Login_Layout", element_justification="C"),
    sg.Column(logged_layout, visible=False, key="Logged_Layout", element_justification="C"),
    sg.Column(file_hub_script_layout, visible=False, key="File_hub_layout", element_justification="C"),
    sg.Column(change_pass_layout, visible=False, key='Change_pass_layout', element_justification="C"),
    sg.Column(userLog_audit_layout, visible=False, key="userLog_audit_layout", element_justification="C")
    ]
]

window = sg.Window("Revenant Version 1.0.0", layout, element_justification="C").Finalize()
window.Maximize()


# Creating the loop to check for events and values
class Main:
    """
    Main class for the application.
    """
    def __init__(self) -> None:
        pass

    def intialize(self):
        """
        Intializes the app.

        Does not return; call on last line.
        """
        # setting needed variables
        username = "0"; password = "0"; count = 0; LAYOUT_CYCLE_VAR = 0; logged_in = False; count = 0; alert = 0; logger = 0; encrypter = 0
        # setting the login class
        login_class = login()
        while True:
            event, values = window.read()
            if event in (None, "Close Window", "Close", "logout", "Close_Audit"):
                logger.log_logout()
                quit()
            if alert == 1:
                sg.popup_auto_close("userLog capacity reached. userLog cleared.", font="Helvetica", non_blocking=True)
            if event == "Ok" and logged_in is False:
                username = values["username"]
                password = values["password"]
                exit_code = login_class.login_sequence(password = password, username=username, count=count)
                if exit_code ==  0:
                    LAYOUT_CYCLE_VAR = 1
                    logged_in = True
                    encrypter = Ciphers(password=password)
                    logger = Log(username)
                    # checking if the 
                elif exit_code == 1:
                    sg.popup_auto_close("The given username is not a valid username.", font="Helvetica", non_blocking=True)
                elif exit_code == 2:
                    sg.popup_auto_close("Incorrect credentials.", font="Helvetica", non_blocking=True)
                    count += 1
                elif exit_code == 3:
                    sg.popup_auto_close("Password or username was not provided.", font="Helvetica", non_blocking=True)
            if LAYOUT_CYCLE_VAR == 1:
                window[f"Login_Layout"].update(visible=False)
                window[f"Logged_Layout"].update(visible=True)
                LAYOUT_CYCLE_VAR = 2
            if event == "file_hub":
                window[f"Logged_Layout"].update(visible=False)
                window[f"File_hub_layout"].update(visible=True)
            elif event == "password_change":
                window[f"Logged_Layout"].update(visible=False)
                window[f"Change_pass_layout"].update(visible=True)
            elif event == "back_pass":
                window[f"Change_pass_layout"].update(visible=False)
                window[f"Logged_Layout"].update(visible=True)
            elif event == "back":
                window[f"File_hub_layout"].update(visible=False)
                window[f"Logged_Layout"].update(visible=True)
            elif event == "Intiate_audit":
                window[f"Logged_Layout"].update(visible=False)
                window[f"File_hub_layout"].update(visible=False)
                window[f"userLog_audit_layout"].update(visible=True)
            elif event == "audit_return":
                window[f"File_hub_layout"].update(visible=True)
                window[f"userLog_audit_layout"].update(visible=False)
            elif event == "file_encrypt":
                # getting file:
                file = sg.popup_get_file("Select the file you wish to encrypt.", font="Helvetica")
                exit_code = encrypter.encrypt(file)
                if exit_code == 0:
                    sg.popup_auto_close("File encryption successful.", font="Helvetica", non_blocking=True)
                elif exit_code == 1:
                    sg.popup_auto_close("File encryption cancelled.", font="Helvetica", non_blocking=True)
                elif exit_code == 2:
                    sg.popup_auto_close("File path is invalid.", font="Helvetica", non_blocking=True)
                elif exit_code == 3:
                    sg.popup_auto_close("App does not have permission to access file.", font="Helvetica", non_blocking=True)
                elif exit_code == 4:
                    sg.popup_auto_close("File is hidden.", font="Helvetica", non_blocking=True)
                elif exit_code == 5:
                    sg.popup_auto_close("File is part of root filesystem and not part of ChromeOS.", font="Helvetica", non_blocking=True)
                elif exit_code == 6:
                    sg.popup_auto_close("File was already encrypted.", font="Helvetica", non_blocking=True)
            elif event == "file_decrypt":
                file = sg.popup_get_file("Select the file you wish to decrypt.", font="Helvetica")
                exit_code = encrypter.decrypt(file)
                if exit_code == 0:
                    sg.popup_auto_close("File decryption successful.", font="Helvetica", non_blocking=True)
                if exit_code == 1:
                    sg.popup_auto_close("File decryption cancelled.", font="Helvetica", non_blocking=True)
                if exit_code == 2:
                    sg.popup_auto_close("File path is invalid.", font="Helvetica", non_blocking=True)
                if exit_code == 3:
                    sg.popup_auto_close("App does not have permission to access file.", font="Helvetica", non_blocking=True)
                if exit_code == 4:
                    sg.popup_auto_close("File is hidden.", font="Helvetica", non_blocking=True)
                if exit_code == 5:
                    sg.popup_auto_close("File is part of root filesystem and not part of ChromeOS.", font="Helvetica", non_blocking=True)
                if exit_code == 6:
                    sg.popup_auto_close("File was encrypted with a different key.", font="Helvetica", non_blocking=True)
                if exit_code == 7:
                    sg.popup_auto_close("File was not encrypted.", font="Helvetica", non_blocking=True)
            elif event == "folder_encrypt":
                folder = sg.popup_get_folder("Select the file you wish to encrypt.", font="Helvetica")
                exit_code = encrypter.encrypt(folder)
                if exit_code == 0:
                    sg.popup_auto_close("Folder encryption successful.", font="Helvetica", non_blocking=True)
                elif exit_code == 1:
                    sg.popup_auto_close("Folder encryption cancelled.", font="Helvetica", non_blocking=True)
                elif exit_code == 2:
                    sg.popup_auto_close("Folder path is invalid.", font="Helvetica", non_blocking=True)
                elif exit_code == 3:
                    sg.popup_auto_close("App does not have permission to access file.", font="Helvetica", non_blocking=True)
                elif exit_code == 4:
                    sg.popup_auto_close("Folder is hidden.", font="Helvetica", non_blocking=True)
                elif exit_code == 5:
                    sg.popup_auto_close("Folder is part of root filesystem and not part of ChromeOS.", font="Helvetica", non_blocking=True)
                elif exit_code == 6:
                    sg.popup_auto_close("Folder was already encrypted.", font="Helvetica", non_blocking=True)
                pass
            elif event == "folder_decrypt":
                folder = sg.popup_get_folder("Select the file you wish to decrypt.", font="Helvetica")
                exit_code = encrypter.decrypt(folder)
                if exit_code == 0:
                    sg.popup_auto_close("Folder decryption successful.", font="Helvetica", non_blocking=True)
                if exit_code == 1:
                    sg.popup_auto_close("Folder decryption cancelled.", font="Helvetica", non_blocking=True)
                if exit_code == 2:
                    sg.popup_auto_close("Folder path is invalid.", font="Helvetica", non_blocking=True)
                if exit_code == 3:
                    sg.popup_auto_close("App does not have permission to access file.", font="Helvetica", non_blocking=True)
                if exit_code == 4:
                    sg.popup_auto_close("Folder is hidden.", font="Helvetica", non_blocking=True)
                if exit_code == 5:
                    sg.popup_auto_close("Folder is part of root filesystem and not part of ChromeOS.", font="Helvetica", non_blocking=True)
                if exit_code == 6:
                    sg.popup_auto_close("Folder was encrypted with a different key.", font="Helvetica", non_blocking=True)
                if exit_code == 7:
                    sg.popup_auto_close("Folder was not encrypted.", font="Helvetica", non_blocking=True)
                pass
            elif event == "vault_encrypt":
                sg.popup_error("501 - NOT YET IMPLEMENTED")
                pass
            elif event == "vault_decrypt":
                sg.popup_error("501 - NOT YET IMPLEMENTED")
                pass
            elif event == "OK_pass":
                old_pass = values["old_password"]
                new_pass = values["new_password"]
                exit_code = login_class.change_password(old_pass, new_pass, username)
                if exit_code == 1:
                    sg.popup_error("You did not give either your old password or new password. Password change automatically cancelled.", font="Helvetica")
                elif exit_code == 2:
                    sg.popup_auto_close("The old password that was entered is wrong. Password change automatically cancelled.", font="Helvetica", non_blocking=True)
                else:
                    encrypter.change_password(exit_code)
                    sg.popup_auto_close("Password Change successful.", font="Helvetica", non_blocking=True)
            elif event == "single_file_log_audit":
                logger.audit("s")
                sg.popup_auto_close("Selected entries cleared.", font="Helvetica", non_blocking=True)
            elif event == "folder_logs_audit":
                logger.audit("f")
                sg.popup_auto_close("Selected entries cleared.", font="Helvetica", non_blocking=True)
            elif event == "vault_log_audit":
                logger.audit("v")
                sg.popup_auto_close("Selected entries cleared.", font="Helvetica", non_blocking=True)
            elif event == "Clear_userlog":
                logger.audit("a")
                sg.popup_auto_close("Selected entries cleared.", font="Helvetica", non_blocking=True)



