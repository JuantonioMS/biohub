#  Constantes para los IDs

ID_LENGTH = 20

ID_CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

ID_PREFIX = {"Subject"  : "bhSubject_",
             "Project"  : "bhProject_",
             "Database" : "bhDatabase_",
             "File"     : "bhFile_",
             "Process"  : "bhProcess_",
             "Pipeline" : "bhPipeline_",
             "Folder"   : "bhFolder_",
             "Unknown"  : "bhID_"}

#  Singularize

SINGULARIZE = {"subjects" : "subject",
               "files"    : "file",
               "folders"  : "folder",
               "processes": "process",
               "pipelines": "pipeline",
               "options"  : "option",
               "inputs"   : "input",
               "outputs"  : "output",
               "outlines" : "outline",
               "tags"     : "tag",
               "links"    : "link"}


#  CLI

DEFAULT_CLI_SEPARATOR = " "

#  Logger

LOG_HEADER = "[log] %(levelname)s :: %(asctime)s"
LOG_BODY = "%(message)s"
LOG_TAIL = "%(filename)s (line %(lineno)s) :: %(name)s\n"

# Alias del entorno conda para BioHub

CONDA_ENVS_PATH = "~/.biohub/conda_envs"

#  Valores por defecto para parámetros relacionados con procesos

DEFAULT_PROCESS_TYPE = "system"

DEFAULT_PROCESS_ENVIROMMENT = "base"

DEFAULT_PROCESS_ROUTE = "common"

DEFAULT_PROCESS_ROLE = "unknown"

DEFAULT_PROCESS_SENTENCE = "<command> <inputs> <options>"

DEFAULT_PROCESS_ROLES_EXCLUDED = {"threads", "outputDirectory"}

DEFAULT_PROCESS_TEMPORAL_NAME = "tmp"

#  Formato por defecto para las fechas

DEFAULT_DATE_FORMAT = "%Y/%b/%d %H:%M:%S"