from biohub.process.wrapper import Option

from biohub.utils import getDefaultRole

from biohub.conf.core.constants.process import PROCESS_DEFAULT_ROUTE, \
                                               PROCESS_OPTIONS_ROLE_CPUTHREADS, \
                                               PROCESS_OPTIONS_ROLE_OUTPUTDIRECTORY


class Options:


    @property
    def defaultOptions(self) -> dict:

        """Get default options for common route and specfic route from conf/apps/<tool>.yaml"""

        auxDefaultOptions = {}

        try: allOptions = self.jsonInfo["options"]
        except KeyError: allOptions = []

        for route in (PROCESS_DEFAULT_ROUTE, self.route):
            for option in allOptions:

                if option["route"] == route:

                    if option["role"] == PROCESS_OPTIONS_ROLE_CPUTHREADS: #  Las opciones referidas al número de procesadores se autocompletan
                        option["value"] = self.threadsPerTask

                    elif option["role"] == PROCESS_OPTIONS_ROLE_OUTPUTDIRECTORY: #  La opción referida al directorio de salida se autocompleta
                        if "value" not in option:
                            option["value"] = self.temporalDirectory

                    auxDefaultOptions[option["role"]] = Option(**option)

        return auxDefaultOptions



    def _setOptions(self, **options) -> dict:

        """Seteo de opciones
        Se buscan las opciones por defecto. Cualquier opción indicada por el usuario eliminará la opción por
        defecto correspondiente si es necesario"""

        self.logger.info(f"OPTIONS :: Wrapping {len(options)} user options")
        userOptions = self.__wrapUserOptions(**options)

        self.logger.info("OPTIONS :: Merge user and default options")
        options = self._mergeOptions(userOptions, self.defaultOptions)

        return options



    def __wrapUserOptions(self, **options) -> dict:

        auxOptions = {}

        for key, value in options.items():

            if isinstance(value, Option): #  El usuario a seteado la opción con el Wrapper
                auxOptions[value.role] = value

            else: #  El usuario ha indicado la opción con el estilo <name> : <value>

                role = getDefaultRole(auxOptions)

                auxOptions[role] = Option(role = role,
                                          name = key,
                                          value = value)

        return auxOptions



    def _mergeOptions(self,
                      userOptions: dict,
                      defaultOptions: dict) -> dict:

        for defaultRole, defaultOption in defaultOptions.items():

            if not defaultRole in [role for role in userOptions.keys()] and \
               not defaultRole in [role for role in userOptions.values()] and \
               not defaultOption.name in [option.name for option in userOptions.values()] and \
               not defaultOption.altName in [option.altName for option in userOptions.values()]:

                userOptions[defaultRole] = defaultOption

        return userOptions