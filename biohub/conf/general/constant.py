#  Constantes para los IDs

ID_LENGTH = 20

ID_CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

ID_PREFIX = {"Subject"  : "bhSubject_",
             "Project"  : "bhProject_",
             "File"     : "bhFile_",
             "Process"  : "bhProcess_",
             "Pipeline" : "bhPipeline_",
             "Unknown"  : "bhID_"}

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