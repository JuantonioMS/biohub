from biohub.process import Process
from biohub.subject import Subject
from biohub.project import Project

from multiprocessing import Pool
import time

class ProcessStoS(Process):

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

            #  Memoria compartida
            if not self.distributedMemory:

                parameters = []
                for subject in self.entity.subjects:

                    parameters.append([subject,
                                       self,
                                       options,
                                       inputs[subject.id] if subject.id in inputs else {},
                                       outputOutlines,
                                       processOutlines,
                                       extraAttrs])

                with Pool(self.simultaneousTasks) as pool:
                    results = pool.starmap(runFuction, parameters)

                aux = {}
                for result, parameter in zip(results, parameters):

                    aux[parameter[0].id] = result

                return aux

            #  Memoria distribuida
            else:

                jobNames = set()

                subjects = [subject.id for subject in self.entity.subjects]

                step = self.coresPerNode // self.coresPerTask

                for index in range(0, len(subjects), step):

                    jobName = f"BHtmp_{index:04}_{self.tool.capitalize()}{self.id}"

                    selectedSubjects = subjects[index : index + step]

                    sbatchOptions = {"--job-name": jobName,
                                     "--ntasks": step * self.coresPerTask,
                                     "--output": f"{jobName}.out"}

                    pythonOrder = ["python -c"]

                    #  Imports
                    pythonOrder += [f"\\\"from {'.'.join(self.__class__.__module__.split('.')[:-1])} import {self.__class__.__name__};",
                                    "from biohub.utils import EntityCreator;"]

                    selectedSubjects = ", ".join([f"'{subject}'" for subject in selectedSubjects])

                    pythonOrder += [f"project = EntityCreator().createProject('BHPRtmp_{self.id}_{index:04}', './{self.entity.path.parent}', subjects = [{selectedSubjects}]);"]

                    #  Process execution
                    pythonOrder += [f"{self.__class__.__name__}(entity = project, simultaneousTasks = {step}, threadsPerTask = {self.threadsPerTask}).run()\\\""]

                    pythonOrder = " ".join(pythonOrder)

                    sbatchOptions["--wrap"] = "\"" + pythonOrder + "\""

                    self.runCommand("sbatch", *[f"{key}={value}" for key, value in sbatchOptions.items()])

                    #jobId = pyslurm.job().submit_batch_job(sbatchOptions)

                    jobNames.add(jobName)


                while True:

                    time.sleep(2)

                    _, output = self.runCommand("squeue --format=\"%.100j\"",
                                                   verbosity = False,
                                                   captureOutput = True)

                    jobs = set(list(map(lambda x: x.strip(), output.split("\n")))[1:-1])

                    if len(jobNames & jobs) == 0:
                        break

                self.runCommand(f"rm *_{self.tool.capitalize()}{self.id}.out")
                self.runCommand(f"rm -rf {self.entity.path.parent}/BHPR_{self.id}_*")

                return {}



def runFuction(subject,
               process,
               options,
               inputs,
               outputOutlines,
               processOutlines,
               extraAttrs):

    result = process.__class__(entity = subject,
                               threads = process.threadsPerTask,
                               save = process.save,
                               duplicate = process.duplicate).run(options = options,
                                                                  inputs = inputs,
                                                                  outputOutlines = outputOutlines,
                                                                  processOutlines = processOutlines,
                                                                  **extraAttrs)
    return result
