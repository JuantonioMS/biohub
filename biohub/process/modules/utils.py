from biohub.utils.wrapper import Option, Input, Output

from biohub.utils import evalSentence

class Utils:


    def findDuplicatedProcesses(self, process) -> list:

        aux = []
        for auxProcess in self.entity.processes.values():

            if process == auxProcess:
                aux.append(auxProcess)

        return aux



    def extractOutputs(self, process) -> dict:

        if not hasattr(process, "entity"):
            process.entity = self.entity

        return {role : output.biohubFile for role, output in process.outputs.items()}



    def _applyEvalSentences(self,
                            inputs: dict = {},
                            outputs: dict = {},
                            options: dict = {},
                            **extraAttrs) -> tuple:

        count = True
        while count:

            count = 0

            for section in options, inputs, outputs: #  Para cada sección que puede variar
                for role, wrap in section.items(): #  Para cada elemento
                    if wrap.evalPending: #  Si tiene sentencias que evaluar

                        for attr in wrap.evalAttributes: #  Para cada atributo que puede tener una sentencia

                            value = getattr(wrap, attr)

                            if isinstance(value, str) and "eval##" in value:

                                sentence = "->" + value.split("->")[1].split("<-")[0] + "<-"

                                try:

                                    result = evalSentence(sentence[2:-2],
                                                          entity = self.entity,
                                                          inputs = inputs,
                                                          outputs = outputs,
                                                          options = options,
                                                          self = self)

                                except (NameError, AttributeError, KeyError, IndexError): break

                                #  Si la sentencia es toda la expresión (puede generar un dato diferente a str)
                                if len(sentence) == len(value):
                                    value = result

                                else: #  Si es una cadena más larga, se remplaza la sentencia por el resultado
                                    value = value.replace(sentence, str(result))

                                #  Actualización del valor en el wrap
                                setattr(wrap, attr, value)

                                if not wrap.evalPending and wrap.condition: #  Si no quedan más sentencias por evaluar

                                    #  Podemos crear el Output completo
                                    if isinstance(wrap, Output):
                                        outputs[role] = self._createOutput(wrap, **extraAttrs)

                                    #  Podemos crear el Input completo
                                    elif isinstance(wrap, Input): inputs[role] = self._createInput(wrap)


                        else: count += 1 #  Añadimos una señal de que algo se ha conseguido

        return inputs, outputs, options


    #%%  5. Purge conditionals__________________________________________________________________________________________


    def _purgeConditionals(self,
                           inputs: dict = {},
                           outputs: dict = {},
                           options: dict = {}):

        aux = {"inputs"  : {},
               "outputs" : {},
               "options" : {}}

        for field, section, dataType in zip(aux.keys(), (inputs, outputs, options), (Input, Output, Option)):

            aux[field] = {key: value for key, value in section.items() \
                                     if isinstance(value, dataType) and value.condition == True}
        return aux["inputs"], aux["outputs"], aux["options"]