from biohub.process import Process
from biohub.container import Subject
from biohub.process.wrapper import Input, Output, Option

import pickle as pkl
from multiprocessing import Pool
import time

class ProcessStoS(Process):


    @staticmethod
    def runWrapper(subject, process,
                   options, inputs,
                   outputOutlines,
                   processOutlines,
                   extraAttrs):

        result = process.__class__(entity = subject,
                                   threadsPerTask = process.threadsPerTask,
                                   save = process.save,
                                   duplicate = process.duplicate)._runBody(options = options,
                                                                           inputs = inputs,
                                                                           outputOutlines = outputOutlines,
                                                                           processOutlines = processOutlines,
                                                                           **extraAttrs)

        return subject.id, result


#%%  Run methods________________________________________________________________________________________________________


    def run(self,
            options: dict = {},
            inputs: dict = {},
            outputOutlines: set = set(),
            processOutlines: set = set(),
            **extraAttrs) -> dict:

        if not self._isBuildCorrect:
            return {}

        #  Proceso único
        if isinstance(self.entity, Subject):
            return self._runSubject(options = options,
                                    inputs = inputs,
                                    outputOutlines = outputOutlines,
                                    processOutlines = processOutlines,
                                    **extraAttrs)

        #  Varios procesos
        else:
            return self._runProject(options = options,
                                    inputs = inputs,
                                    outputOutlines = outputOutlines,
                                    processOutlines = processOutlines,
                                    **extraAttrs)


#%%  Run subject methods________________________________________________________________________________________________


    def _runSubject(self,
                    options: dict = {},
                    inputs: dict = {},
                    outputOutlines: set = set(),
                    processOutlines: set = set(),
                    **extraAttrs):

        return super().run(options = options,
                           inputs = inputs,
                           outputOutlines = outputOutlines,
                           processOutlines = processOutlines,
                           **extraAttrs)


#%%  Run project methods________________________________________________________________________________________________


    def _runProject(self,
                    options: dict = {},
                    inputs: dict = {},
                    outputOutlines: set = set(),
                    processOutlines: set = set(),
                    **extraAttrs):


        self._runHead(options = options,
                      inputs = inputs,
                      outputOutlines = outputOutlines,
                      processOutlines = processOutlines,
                      **extraAttrs)


        if not self.distributedMemory:

            output = self._runProjectSharedMemory(options = options,
                                                  inputs = inputs,
                                                  outputOutlines = outputOutlines,
                                                  processOutlines = processOutlines,
                                                  **extraAttrs)

        else:

            output = self._runProjectDistributedMemory(options = options,
                                                       inputs = inputs,
                                                       outputOutlines = outputOutlines,
                                                       processOutlines = processOutlines,
                                                       **extraAttrs)


        self._runTail(options = options,
                      inputs = inputs,
                      outputOutlines = outputOutlines,
                      processOutlines = processOutlines,
                      **extraAttrs)


        return output


#%%  Shared memory methods______________________________________________________________________________________________


    def _runProjectSharedMemory(self,
                                options: dict = {},
                                inputs: dict = {},
                                outputOutlines: set = set(),
                                processOutlines: set = set(),
                                **extraAttrs):

        parameters = []

        for subject in self.entity.subjects:

            auxInputs = {}
            for role, value in inputs.items():

                if isinstance(value, dict) and subject.id in value:
                    auxInputs[role] = value[subject.id]

                else:
                    auxInputs[role] = value

            parameters.append([subject,
                                self,
                                options,
                                auxInputs,
                                outputOutlines,
                                processOutlines,
                                extraAttrs])

        with Pool(self.concurrentTasks) as pool:
            results = pool.starmap(self.runWrapper, parameters)

        aux = {}
        for subject, outputs in results:
            aux[subject] = outputs

        return aux


#%%  Distributed memory methods_________________________________________________________________________________________


    def _runProjectDistributedMemory(self,
                                     options: dict = {},
                                     inputs: dict = {},
                                     outputOutlines: set = set(),
                                     processOutlines: set = set(),
                                     **extraAttrs):

        jobNames = set()
        pklNames = set()

        for subject in self.entity.subjects:

            jobName = f"BioHub_{self.tool.capitalize()}_{subject.id}_{self.id}"


            sbatchParameters = {"--job-name" : jobName,
                                "--ntasks"   : self.threadsPerTask // self.threadsPerCore,
                                "--mem"      : self.memoryPerTask,
                                "--time"     : self.timePerTask,
                                "--output"   : f".{jobName}.out"}

            #  Imports
            importSentence = ["import pickle as pkl",
                              "from biohub.container import Subject, Project, Database",
                              "from biohub.storage import File, Folder",
                              "from biohub.process.wrapper import Input, Output, Option",
                              f"from {'.'.join(self.__class__.__module__.split('.')[:-1])} import {self.__class__.__name__}"]

            #  Subject
            subjectSentence = [f"subject = Subject(path = './{self.entity.path.parent}/../subjects/{subject.id}/biohub_subject.xml')"]

            #  Process execution
            subjectInputs, subjectOptions = self.splitWrappers(subject, inputs, options)

            pklName = f"{subject.id}_{self.id}.pkl"

            with open(f".inputs_{pklName}", "wb") as pklFile:
                pkl.dump(subjectInputs, pklFile)

            with open(f".options_{pklName}", "wb") as pklFile:
                pkl.dump(subjectOptions, pklFile)

            with open(f".outputOutlines_{pklName}", "wb") as pklFile:
                pkl.dump(outputOutlines, pklFile)

            with open(f".processOutlines_{pklName}", "wb") as pklFile:
                pkl.dump(processOutlines, pklFile)

            with open(f".extraAttrs_{pklName}", "wb") as pklFile:
                pkl.dump(extraAttrs, pklFile)

            processSentence = ["".join(["output = ",
                                        f"{self.__class__.__name__}",
                                        f"(entity = subject, threadsPerTask = {self.threadsPerTask})",
                                        f"._runBody(inputs = pkl.load(open('.inputs_{pklName}', 'rb'))",
                                        f", options = pkl.load(open('.options_{pklName}', 'rb'))",
                                        f", outputOutlines = pkl.load(open('.outputOutlines_{pklName}', 'rb'))",
                                        f", processOutlines = pkl.load(open('.processOutlines_{pklName}', 'rb'))",
                                        f", **pkl.load(open('.extraAttrs_{pklName}', 'rb'))",
                                        f")"])]

            outputSentence = [f"outputPkl = open('.outputs_{pklName}', 'wb')",
                              f"pkl.dump(output, outputPkl)",
                              "outputPkl.close()"]

            pythonSentence = "python -c \\\"" + "; ".join(importSentence +\
                                                          subjectSentence +\
                                                          processSentence +\
                                                          outputSentence) + "\\\""

            sbatchParameters["--wrap"] = "\"" + pythonSentence + "\""

            self.runCommand("sbatch", *[f"{key}={value}" for key, value in sbatchParameters.items()])

            jobNames.add(jobName)
            pklNames.add(pklName)

        #  Todos los trabajos lanzados, bucle para esperar a que todos terminen
        while True:

            time.sleep(10) #  Checkear cada 10 segundos

            _, output = self.runCommand("squeue --nohead --format %j",
                                        verbosity = False)

            jobs = set(list(map(lambda x: x.strip(), output.split("\n"))))

            if len(jobNames & jobs) == 0: #  Si no quedan trabajos en cola
                break

        #  Recuperar los outputs
        outputs = {}
        for pklName in pklNames:
            output = pkl.load(open(f".outputs_{pklName}", "rb"))

            for key, value in output.items():
                if not key in outputs: outputs[key] = {"_".join(pklName.split("_")[:2]) : value}
                else: outputs[key]["_".join(pklName.split("_")[:2])] = value

        #  Borrando todos los archivos intermedios
        self.runCommand(f"rm .*{self.id}.*")

        return outputs


    @staticmethod
    def splitWrappers(subject: Subject, inputs: dict, options: dict) -> dict:

        aux = []

        for wrap in (inputs, options):
            auxWrap = {}

            for role, value in wrap.items():

                if isinstance(value, dict) and subject.id in value: #  Un input por sujeto
                    auxWrap[role] = value[subject.id]

                elif isinstance(value, (Input, Option)): #  Un input general para todos los sujetos
                    auxWrap[role] = value

                else: raise TypeError(f"{type(value)} not valid as an input/option")

            aux.append(auxWrap)

        return aux