from pathlib import Path

#  CORE_________________________________________________________________________________________________________________

PATH_BIOHUB_DIRECTORY = Path(Path.home(), ".biohub")

#  CONDA________________________________________________________________________________________________________________

PATH_CONDA_ENVS = Path(PATH_BIOHUB_DIRECTORY, "conda_envs")

#  SINGULARITY__________________________________________________________________________________________________________

PATH_SINGULARITY_IMAGES = Path(PATH_BIOHUB_DIRECTORY, "singularity_imgs")


PATH_CONF = Path(__file__).parent.parent.parent
PATH_CONF_APPS = Path(PATH_CONF, "apps")
PATH_CONF_CORE = Path(PATH_CONF, "core")
PATH_CONF_CORE_SCHEMAS = Path(PATH_CONF_CORE, "schemas")
PATH_CONF_CORE_SCHEMAS_APPS = Path(PATH_CONF_CORE_SCHEMAS, "apps.json")