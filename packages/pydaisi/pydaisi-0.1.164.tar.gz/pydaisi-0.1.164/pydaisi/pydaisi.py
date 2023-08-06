import requests
import os
import uuid
import shutil
import sys
import random
import codecs
import dill
import json

from importlib import util
from dotenv import load_dotenv

load_dotenv()

sandy_base_url = "https://app.daisi.io"
headers = {"Authorization": "token " + os.getenv("ACCESS_TOKEN", "")}


def load_dill_string(s):  # pragma: no cover
    return dill.loads(codecs.decode(s.encode(), "base64"))


def get_dill_string(obj):  # pragma: no cover
    return codecs.encode(dill.dumps(obj), "base64").decode()


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


class Daisi:
    """
    A utility to assist in developing Daisis for the Sandy platform.

    A tool for creating, validating, publishing, and updating daisis.

    :param daisi_id: A daisi name or UUID
    :param base_url: The default URL to use for connecting to the daisi
    """

    def __init__(self, daisi_id=None, base_url=sandy_base_url):
        """
        Daisi constructor method.

        :param daisi_id:  A Daisi name or UUID

        :raises ValueError: DaisiID Not Found (Non-200 response)
        """
        self.uuid = None
        self.name = None
        self.description = None
        self.base_url = base_url + "/pebble-cli-api/pebbles"
        self.data_mapping = {}

        if not daisi_id:
            self.name = self.random_name()
            daisi_id = self.name

        # Check if it's a valid uuid:
        try:
            check_uuid = uuid.UUID(daisi_id) == uuid.UUID("{" + daisi_id + "}")
        except Exception as e:
            check_uuid = False

        if check_uuid:
            r = requests.get(self.base_url + "/" + daisi_id, headers=headers)
            if r.status_code != 200:
                raise ValueError("The specified Daisi ID could not be found.")
            else:
                print("Found existing Daisi: " + r.json()["name"])

                self.name = r.json()["name"]
                self.uuid = daisi_id
        else:
            print("Calling " + self.base_url + "/search?query=" + daisi_id)
            r = requests.get(
                self.base_url + "/search?query=" + daisi_id, headers=headers
            )
            result = r.json()

            if result:
                self.name = daisi_id
                daisi_id = result[0]["id"]
                print("Found existing Daisi: " + daisi_id)
                self.uuid = daisi_id
            else:
                # TODO: Handle git repo connection here
                raise ValueError("That daisi could not be found.")


    def chain(self, args):
        """
        Collects reusable outputs from the output of another daisi.

        :param args: A dictionary of arguments used in the chain.
        :type args: dict

        :return: A clean dictionary to be used as daisi input
        :rtype dict
        """
        # Set all the arguments as provided
        clean_args = args

        # Parse the arguments
        # for argument_name, argument_value in args.items():

        #     # If the argument is a daisi output, we must chain the data
        #     if type(argument_value) == list:

        #         # Assume it's the first output
        #         try:
        #             clean_args[argument_name] = argument_value[0]["data"]

        #             # Check whether the ids of outputs match
        #             for arg in argument_value:

        #                 # If the id of a particular output matches the argument name, set the value
        #                 if arg["id"].startswith(argument_name) or argument_name.startswith(
        #                     arg["id"]
        #                 ):
        #                     clean_args[argument_name] = arg["data"]
        #         except:
        #             continue

        return clean_args


    def compute(self, func="compute", **args):
        # Check whether any of the arguments are daisis
        parsed_args = self.chain(args)
        parsed_args = self.pickle_hidden(args)

        parsed_args["_endpoint"] = func

        # Call the specified Daisi compute
        r = requests.post(
            self.base_url + "/" + self.uuid + "/compute", json=parsed_args, headers=headers
        )

        result = None
        if r.status_code == 200:
            result = self.unpickle_hidden(r.json())

        return result


    def schema(self):
        """
        Query the Daisi schema from the Sandy platform.

        :return: Resulting schema if found, None if not found
        :rtype list
        """
        # Call the specified Daisi schema
        r = requests.get(self.base_url + "/" + self.uuid + "/schema", headers=headers)

        result = None
        if r.status_code == 200:
            result = r.json()

        return result


    def unpickle_hidden(self, output):
        final_output=[]
        for out in [y["data"] for y in output["outputs"]]:
            if type(out) == str and out.startswith("lookup:"):
                # Get the binary data
                l_split = out.split("lookup:")

                r = requests.get(
                    self.base_url + "/pickle?lookup=" + l_split[1], headers=headers
                )

                out = load_dill_string(r.content.decode())

                final_output.append(out)
            else:
                final_output.append(out)

        return final_output


    def store_pickle(self, data):
        my_args = {"data": data}

        # Call the specified Daisi compute
        r = requests.post(
            self.base_url + "/pickle", json=my_args, headers=headers
        )

        # Return the result
        return r.content.decode()


    def pickle_hidden(self, args):
        final_args={}
        for k, v in args.items():
            if not is_jsonable(v):
                x = self.store_pickle(get_dill_string(v))
                final_args[k] = "lookup:" + x
            else:
                final_args[k] = v

        return final_args


    @staticmethod
    def get_daisis(base_url=sandy_base_url):
        """
        Queries Sandy platform for a list of all current daisis.

        :return: List of daisis available on the Sandy platform.
        :rtype list
        """

        r = requests.get(base_url + "/pebble-cli-api/pebbles" + "?pageSize=10000", headers=headers)
        result = r.json()

        return_list = []
        for daisi in result["pebbles"]:
            return_list.append(
                {
                    "id": daisi["id"],
                    "name": daisi["name"],
                    "description": daisi["description"],
                }
            )

        final_return = sorted(return_list, key=lambda x: x["name"])

        return final_return
