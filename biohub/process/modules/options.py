from biohub.process.wrapper import Option

from biohub.utils import getDefaultRole

from biohub.conf.general.constant import DEFAULT_PROCESS_ROUTE
class Options:


    @property
    def defaultOptions(self) -> dict:

        """Get default options for common route and specfic route from conf/apps/<tool>.yaml"""

        auxDefaultOptions = {}

        try: allOptions = self.jsonInfo["options"]
        except KeyError: allOptions = []

        for route in (DEFAULT_PROCESS_ROUTE, self.route):
            for option in allOptions:

                if option["role"] == route:

                    if option["role"] == "threads": #  Las opciones referidas al número de procesadores se autocompletan
                        option["value"] = self.threadsPerTask

                    elif option["role"] == "outputDirectory": #  La opción referida al directorio de salida se autocompleta
                        if "value" not in option:
                            option["value"] = self.temporalDirectory

                    auxDefaultOptions[option["role"]] = Option(**option)

        return auxDefaultOptions



    def _setOptions(self, **options) -> dict:

        """Seteo de opciones
        Se buscan las opciones por defecto. Cualquier opción indicada por el usuario eliminará la opción por
        defecto correspondiente si es necesario"""

        auxOptions = {}

        self.logger.info(f"OPTIONS :: Wrapping {len(options)} user options")

        for key, value in options.items():

            if isinstance(value, Option): #  El usuario a seteado la opción con el Wrapper
                auxOptions[value.role] = value

            else: #  El usuario ha indicado la opción con el estilo <name> : <value>

                role = getDefaultRole(auxOptions)

                auxOptions[role] = Option(role = role,
                                          name = key,
                                          value = value)

        self.logger.info("OPTIONS :: Completing  with default options")

        rolesToDel = []
        for defaultRole, defaultOption in self.defaultOptions.items():

            #  Chequeando si el nombre de alguna opción por defecto se ha escrito en las opciones del usuario
            if not any([defaultOption.name in [userOption.name for userOption in auxOptions.values()],
                        defaultOption.alternativeName in [userOption.name for userOption in auxOptions.values()]]):

                #  No se ha detectado el nombre en las opciones del usuario
                auxOptions[defaultRole] = defaultOption


            else:
                #  Se ha detectado el nombre
                for userRole, userOption in auxOptions.items():

                    #  Se intenta completar la información de la opción con la que se tiene por defecto
                    if any([defaultOption.name == userOption.name, defaultOption.alternativeName == userOption.name]):

                        userOption._role = defaultOption.role #  Corrige el rol
                        userOption._alternativeName = defaultOption.alternativeName #  Rellena el nombre alternativo

                        auxOptions[defaultRole] = userOption #  Guarda la opción completa
                        rolesToDel.append(userRole) #  Anotamos el rol antiguo para borrarlo después

        #  Eliminando las opciones que no tienen toda la información completa
        for roleToDel in rolesToDel:
            del auxOptions[roleToDel]

        self.logger.info(f"OPTIONS :: Number of options setted {len(auxOptions)}")

        return auxOptions