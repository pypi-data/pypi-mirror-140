#!/usr/bin/python3
import datetime
import json
import os

import pyrebase


class FailedLoadingAuthFileException(Exception):
    """
    If we cant load the auth file for some reason.
    """

    def __init__(self, message="Unknown", errors={}):
        super().__init__(message)
        self.errors = errors


kEpoch = datetime.datetime.utcfromtimestamp(0)


def unix_time_now_seconds():
    return (datetime.datetime.utcnow() - kEpoch).total_seconds()


class Authentication(object):

    kAuthPath = "./auth.json"
    kFirebaseConfig = {
        "apiKey": "AIzaSyDKAuaWu9qPNHU0Y9gACRDv3Esj6T8w3kE",
        "authDomain": "canarid-621aa.firebaseapp.com",
        "databaseURL": "https://canarid-621aa.firebaseio.com",
        "storageBucket": "",
    }

    def printifv(self, msg):
        if self._verbose:
            print(f"[Authentication] {msg}")

    def __init__(
        self,
        generate_new: bool = False,
        verbose: bool = False,
        auth_path: str = kAuthPath,
        skip_refresh_on_init=False,
    ):
        """
        Constructor
        :param generate_new: Will prompt the user to create a new third-party token rather than refreshing an existing one.
        :param verbose: If we should display extra info
        :param auth_path: Path to the locally cached authentication information
        :param skip_refresh_on_init: By default we refresh the token if needed upon object construction
        """
        self._auth_path = auth_path if auth_path else self.kAuthPath
        self._verbose = verbose

        self.printifv(f"Loading authentication from {os.path.abspath(self._auth_path)}")

        self._firebase = pyrebase.initialize_app(self.kFirebaseConfig)

        # Cached file deets
        self._id_token = None
        self._refresh_token = None
        self.maybe_id_token_expire_time = None

        #
        # If the user requested to generate a new third-party token/file. Help em out dude.
        #
        if generate_new:
            self._generate_new()

        #
        # Do the typical refreshing now (load file, if time is past then refresh the file)
        #
        if not skip_refresh_on_init:
            self.refresh()

        self.printifv("Complete.")

    # ##############################################################################
    # Public API
    # ##############################################################################

    def refresh(self):
        #
        # Try to load up the file
        #
        try:
            (
                self._id_token,
                self._refresh_token,
                self.maybe_id_token_expire_time,
            ) = self._load_file()
        except FailedLoadingAuthFileException as e:
            raise FailedLoadingAuthFileException(
                f"Failed to read authentication file. Please run the authentication refresh with 'generate' option generate a new third-party token and authentication file. ({str(e)})"
            )

        #
        # If it looks like the timer for expiration has passed or is close, ask for a refresh
        #
        if unix_time_now_seconds() - self.maybe_id_token_expire_time > 60 * 50:
            self.printifv("Refreshing token...")
            refresh_result = self._firebase.auth().refresh(self._refresh_token)
            self.printifv("Updating locally stored credentials...")
            self._write_file(
                refresh_result["idToken"],
                refresh_result["refreshToken"],
                unix_time_now_seconds(),
            )
            return True
        else:
            self.printifv(
                "Looks like the token has been refreshed recently enough. not refreshing"
            )
            return False

    def get_secret_token_id(self):
        return self._id_token

    # ##############################################################################
    # Private Helpers
    # ##############################################################################
    def _generate_new(self):
        custom_token = input(
            "Please use https://REDACTED to generate a new token. Paste it here: "
        )

        self.printifv("Retreiving updated credentials...")
        custom_token_result = self._firebase.auth().sign_in_with_custom_token(
            custom_token
        )

        id_token = custom_token_result["idToken"]
        refresh_token = custom_token_result["refreshToken"]
        # note this is okay to store this here, we're just optimizing the refresh query
        maybe_id_token_expire_time = unix_time_now_seconds()

        self._write_file(id_token, refresh_token, maybe_id_token_expire_time)

    def _write_file(self, id_token, refresh_token, maybe_id_token_expire_time):
        """
        This creates or overwrites
        """
        try:
            os.remove(self._auth_path)
        except:
            pass
        with open(self._auth_path, "w") as auth_file:
            json.dump(
                {
                    "id_token": id_token,
                    "refresh_token": refresh_token,
                    "maybe_id_token_expire_time": maybe_id_token_expire_time,
                },
                auth_file,
            )

    def _load_file(self):
        """
        Try to load details from the authentication file

        :raises FailedLoadingAuthFileException
        """
        if not os.path.exists(self._auth_path):
            raise FailedLoadingAuthFileException(
                f"File does not exist: {self._auth_path}"
            )

        with open(self._auth_path) as auth_file:
            id_token, refresh_token, maybe_id_token_expire_time = (None, None, None)
            try:
                keys = json.load(auth_file)
                id_token = keys["id_token"]
                refresh_token = keys["refresh_token"]
                maybe_id_token_expire_time = keys["maybe_id_token_expire_time"]
            except:
                raise FailedLoadingAuthFileException(
                    f"Corrupt: could not read required keys: {self._auth_path}"
                )

        return id_token, refresh_token, maybe_id_token_expire_time
