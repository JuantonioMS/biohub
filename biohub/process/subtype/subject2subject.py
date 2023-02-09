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
            if not self.nodes:

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

                for index, subject in enumerate(self.entity.subjects):

                    sbatchOptions = {"job-name": f"BHtmp_{index:03}_{self.id}",
                                     "ntasks": 1,
                                     "cpus-per-task": self.coresPerTask,
                                     "output": f"BHtmp_{index:03}_{self.id}.out",
                                     "mem": "10GB"}

                    pythonOrder = ["python -c"]

                    #  Imports
                    pythonOrder += [f"\"from {'.'.join(self.__class__.__module__.split('.')[:-1])} import {self.__class__.__name__};",
                                    "from biohub.subject import Subject;"]

                    #  Load subject
                    pythonOrder += [f"subject = Subject(path = '{self.entity.path.parent.parent}/subjects/{subject.id}/biohub_subject.xml');"]

                    #  Process execution
                    pythonOrder += [f"{self.__class__.__name__}(entity = subject, threads = {self.threadsPerTask}).run()\""]

                    pythonOrder = " ".join(pythonOrder)

                    sbatchOptions["wrap"] = pythonOrder

                    jobId = pyslurm.job().submit_batch_job(sbatchOptions)

                    jobIds.add(jobId)

                while True:

                    time.sleep(10)

                    jobs = set(pyslurm.job().get().keys())

                    if len(jobIds & jobs) == 0:
                        break

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
