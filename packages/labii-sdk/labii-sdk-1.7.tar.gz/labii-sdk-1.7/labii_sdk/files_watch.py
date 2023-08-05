from api import *
import os, json

def files_watch(configuration_file="configuration.json"):
    """
    """
    # collect configuration
    configuration = collect_configuration(configuration_file)
    

def collect_configuration(configuration_file):
    """
    """
    # read configuration.json
    configuration = {}
    if os.path.isfile(configuration_file):
        with open(configuration_file) as json_file:
            configuration = json.load(json_file)
    # collect email and password
    for i in ["email", "password"]:
        if not i in configuration:
            v = input(f"{i.title()}: ")
            configuration[i] = v
    # update the configuration
    with open(configuration_file, 'w') as outfile:
        json.dump(d, outfile)
    return configuration
