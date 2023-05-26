from datetime import datetime

from pathlib import Path

import yaml

from biohub.conf.general.constant import SINGULARIZE

#  _________________________Utilitiy functions_________________________



def singularize(word):
    return SINGULARIZE[word.lower()]



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