from biohub.process import Process
from biohub.container import Subject

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

        return result


    def run(self,
            options: dict = {},
            inputs: dict = {},
            outputOutlines: set = set(),
            processOutlines: set = set(),
            **extraAttrs) -> dict:

        #  Proceso único
        if isinstance(self.entity, Subject):

            return super().run(options = options,
                               inputs = inputs,
                               outputOutlines = outputOutlines,
                               processOutlines = processOutlines,
                               **extraAttrs)

        #  Varios procesos
        else:

            self._runHead(options = options,
                            inputs = inputs,
                            outputOutlines = outputOutlines,
                            processOutlines = processOutlines,
                            *extraAttrs)

            #  Memoria compartida
            if not self.distributedMemory:

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
                #for result, parameter in zip(results, parameters):

                    #aux[parameter[0].id] = result

            #  Memoria distribuida
            else:

                jobNames = set()

                for subject in self.entity.subjects:

                    jobName = f"BioHub_{self.tool.capitalize()}_{subject.id}_{self.id}"

                    #selectedSubjects = subjects[index : index + step]

                    sbatchOptions = {"--job-name" : jobName,
                                     "--ntasks" : self.threadsPerTask // self.threadsPerCore,
                                     "--mem" : self.memoryPerTask,
                                     "--time" : self.timePerTask,
                                     "--output": f"{jobName}.out"}

                    pythonOrder = ["python -c"]

                    #  Imports
                    pythonOrder += [f"\\\"from {'.'.join(self.__class__.__module__.split('.')[:-1])} import {self.__class__.__name__};", #  Tool import
                                    "from biohub.subject import Subject;"]  #  Subject import

                    #pythonOrder += [f"\\\"from {'.'.join(self.__class__.__module__.split('.')[:-1])} import {self.__class__.__name__};",
                    #               "from biohub.utils import EntityCreator;"]

                    #selectedSubjects = ", ".join([f"'{subject}'" for subject in selectedSubjects])

                    pythonOrder += [f"subject = Subject(path = './{self.entity.path.parent}/../subjects/{subject.id}/biohub_subject.xml');"]
                    #pythonOrder += [f"project = EntityCreator().createProject('BHPRtmp_{self.id}_{index:04}', './{self.entity.path.parent}', subjects = [{selectedSubjects}]);"]

                    #  Process execution
                    pythonOrder += [f"{self.__class__.__name__}(entity = subject, threadsPerTask = {self.threadsPerTask}).run()\\\""]
                    #pythonOrder += [f"{self.__class__.__name__}(entity = project, simultaneousTasks = {step}, threadsPerTask = {self.threadsPerTask}).run()\\\""]

                    pythonOrder = " ".join(pythonOrder)

                    sbatchOptions["--wrap"] = "\"" + pythonOrder + "\""

                    self.runCommand("sbatch", *[f"{key}={value}" for key, value in sbatchOptions.items()])

                    #jobId = pyslurm.job().submit_batch_job(sbatchOptions)

                    jobNames.add(jobName)



                while True:

                    time.sleep(2)

                    _, output = self.runCommand("squeue --format=\"%.100j\"",
                                                   verbosity = False)

                    jobs = set(list(map(lambda x: x.strip(), output.split("\n")))[1:-1])

                    if len(jobNames & jobs) == 0:
                        break

                self.runCommand(f"rm *_{self.id}.out")


            self._runTail(options = options,
                            inputs = inputs,
                            outputOutlines = outputOutlines,
                            processOutlines = processOutlines,
                            *extraAttrs)


            return {}