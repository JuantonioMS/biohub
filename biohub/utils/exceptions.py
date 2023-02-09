class UnmatchingFileError(Exception):

    def __init__(self, parameters, msg = ""):

        if not msg:
            parameters = [f"{key}: {value}" for key, value in parameters.items()]
            parameters = ";".join(parameters)

            msg = f"No file found for parametes -> {parameters}"

        super().__init__(msg)


class MultipleMatchingFilesError(Exception):

    def __init__(self, candidates, parameters, msg = ""):

        if not msg:
            parameters = [f"{key}: {value}" for key, value in parameters.items()]
            parameters = ";".join(parameters)

            msg = f"Multiple files ({len(candidates)}) found for parametes -> {parameters}"

        super().__init__(msg)