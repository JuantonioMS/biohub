from biohub.process import Process
from biohub.subject import Subject
from biohub.project import Project

from multiprocessing import Pool
import random
import pyslurm
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

                jobIds = set()

                subjects = [subject.id for subject in self.entity.subjects]

                for index in range(0, len(subjects), (step := self.coresPerNode // self.coresPerTask)):

                    selectedSubjects = subjects[index : index + step]

                    sbatchOptions = {"job-name": f"BHtmp_{index:03}_{self.id}",
                                     "ntasks": 1,
                                     "cpus-per-task": self.coresPerTask,
                                     "output": f"BHtmp_{index:03}_{self.id}.out"}

                    pythonOrder = ["python -c"]

                    #  Imports
                    pythonOrder += [f"\"from {'.'.join(self.__class__.__module__.split('.')[:-1])} import {self.__class__.__name__};",
                                    "from biohub.utils import EntityCreator;"]

                    selectedSubjects = ", ".join([f"'{subject}'" for subject in selectedSubjects])

                    pythonOrder += [f"project = EntityCreator().createProject('BHPRtmp_{self.id}_{index:03}', './{self.entity.path.parent}', subjects = [{selectedSubjects}]);"]

                    #  Process execution
                    pythonOrder += [f"{self.__class__.__name__}(entity = project, simultaneousTasks = {step}, threadsPerTask = {self.threadsPerTask}).run()\""]

                    pythonOrder = " ".join(pythonOrder)

                    sbatchOptions["wrap"] = pythonOrder

                    jobId = pyslurm.job().submit_batch_job(sbatchOptions)

                    jobIds.add(jobId)

                while True:

                    time.sleep(2)

                    jobs = set(pyslurm.job().get().keys())

                    print("Jobs remaining:", len(jobIds & jobs))
                    if len(jobIds & jobs) == 0:
                        break

                self.runCommand(f"rm *_{self.id}.out")
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
