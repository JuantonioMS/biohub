from biohub.utils.wrapper import Option

class Options:


    @property
    def defaultOptions(self) -> dict:

        """Get default options for common route and specfic route from conf/apps/<tool>.yaml"""

        auxDefaultOptions = {}

        try: allOptions = self.jsonInfo["options"]
        except KeyError: allOptions = []

        for element in allOptions:

            if element["route"] in ("common", self.route):

                if element["role"] == "threads":
                    element["value"] = self.threadsPerTask

                elif element["role"] == "outputDirectory":
                    element["value"] = self.temporalDirectory

                auxDefaultOptions[element["role"]] = Option(**element)

        return auxDefaultOptions



    def _setOptions(self, **options) -> dict:

        """Seteo de opciones
        Se buscan las opciones por defecto. Cualquier opción indicada por el usuario eliminará la opción por
        defecto correspondiente si es necesario"""

        self.entity.logger.info(f"Process {self.id} :: OPTIONS :: {len(options)} user options")

        auxOptions = {}
        count = 1
        for key, value in options.items():

            if isinstance(value, Option): #  El usuario a seteado la opción con el Wrapper
                options[value.role] = value

            else: #  El usuario ha indicado la opción con el estilo <name> : <value>
                options[f"unknown_{count}"] = Option(role = f"unknown_{count}",
                                                     name = key,
                                                     value = value)
                count += 1



        rolesToDel = []
        for defaultRole, defaultOption in self.defaultOptions.items():


            if not any([defaultOption.name in [userOption.name for userOption in options.values()],
                        defaultOption.alternativeName in [userOption.name for userOption in options.values()]]):

                auxOptions[defaultRole] = defaultOption


            else:
                for userRole, userOption in options.items():
                    if any([defaultOption.name == userOption.name, defaultOption.alternativeName == userOption.name]):

                        userOption._role = defaultOption.role
                        userOption._alternativeName = defaultOption.alternativeName

                        options[defaultRole] = userOption
                        rolesToDel.append(userRole)

        for roleToDel in rolesToDel:
            del options[roleToDel]

        auxOptions.update(options)

        self.entity.logger.info(f"Process {self.id} :: OPTIONS :: {len(auxOptions)} setted options")

        return auxOptions