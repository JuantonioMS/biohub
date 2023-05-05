from datetime import datetime

from pathlib import Path

import yaml


#  _________________________Utilitiy functions_________________________


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


    def evalSentence(self, sentence, **kwargs):

        locals().update(kwargs) #  Actualiza las variables locales

        return eval(sentence[6:])

def evalSentence(sentence, **kwargs):

    locals().update(kwargs) #  Actualiza las variables locales

    return eval(sentence[6:] if "eval##" in sentence else sentence)


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