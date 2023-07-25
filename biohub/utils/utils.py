from datetime import datetime

from pathlib import Path

import yaml

from biohub.conf.core.constants.process import PROCESS_DEFAULT_ROLE
from biohub.conf.core.constants.core import CORE_SINGULARIZE


#  _________________________Utilitiy functions_________________________


def getDefaultRole(context):

    count = 1

    while True:

        if candidate := f"{PROCESS_DEFAULT_ROLE} {count}" in context: count += 1
        else: return candidate


def singularize(word):
    return CORE_SINGULARIZE[word.lower()]



def readYaml(file):

    try:

        with open(file, "r") as yamlFile:

            data = yaml.load(yamlFile, Loader = yaml.SafeLoader)

        return data

    except FileNotFoundError: return {}



def verifyPath(path):

    if not isinstance(path, Path):
            path = Path(path)

    return path



def verifyDate(date: str) -> datetime:

    if not isinstance(date, datetime):
        date = datetime.strptime(date, "%d/%m/%Y;%H:%M:%S")

    return date



def evalSentence(sentence, **kwargs):

    from biohub.conf.core.constants.id import ID_CHARACTERS, \
                                              ID_LENGTH, \
                                              ID_PREFIX

    from biohub.conf.core.constants.path import PATH_BIOHUB_DIRECTORY, \
                                                PATH_CONDA_ENVS, \
                                                PATH_CONF, \
                                                PATH_CONF_APPS, \
                                                PATH_CONF_CORE, \
                                                PATH_CONF_CORE_SCHEMAS, \
                                                PATH_CONF_CORE_SCHEMAS_APPS, \
                                                PATH_SINGULARITY_IMAGES, \
                                                PATH_SYSTEM_FOLDERS

    locals().update(kwargs) #  Actualiza las variables locales

    while isinstance(sentence, str) and "eval##" in sentence:

        fragment = sentence.split("->")[1].split("<-")[0][6:]

        evaluation = eval(fragment)

        if len(fragment) + 10 == len(sentence): #  Si el fragmento es la sentencia entera (puede devolver no str)
            return evaluation

        else:
            sentence = sentence.replace(f"->eval##{fragment}<-",
                                        str(evaluation))

    return sentence



def isThisWordThere(word: str,
                    place: dict) -> bool:

    return any(word == word for key in place for word in place[key])



def completeNestedDict(brick: dict,
                       wall: dict,
                       concrete: str):

    if len(wall) == 0:
        wall = dict([(key, dict()) for key in brick.keys()])


    for key, value in brick.items():
        wall[key][concrete] = value

    return wall