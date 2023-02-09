from biohub.process import Process
from biohub.subject import Subject
from biohub.project import Project

from multiprocessing import Pool
import random

class ProcessStoS(Process):

    def run(self,
            options: dict = {},
            inputs: dict = {},
            outputOutlines: set = set(),
            processOutlines: set = set(),
            **extraAttrs) -> dict:

        if isinstance(self.entity, Subject):

            return super().run(options = options,
                               inputs = inputs,
                               outputOutlines = outputOutlines,
                               processOutlines = processOutlines,
                               **extraAttrs)

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

                with Pool(self.threads // self.coresPerTask) as pool:


                    results = pool.starmap(runFuction, parameters)

                aux = {}
                for result, parameter in zip(results, parameters):

                    aux[parameter[0].id] = result

                return aux

            #  Memoria distribuida
            else:

                for index in range(0, len(self.entity.subjects), self.tasksPerNode):

                    subjects = [subject.id for subject in self.entity.subjects[index : index + self.tasksPerNode]]

                    jobName = f"BHtmp_{index:02}_{random.randint(0, 99):02}"

                    #  sbatch
                    preamble = ["#!/bin/sh",
                                f"#SBATCH --ntasks={self.coresPerTask}",
                                f"#SBATCH--job-name={jobName}"]

                    preamble = "\n".join(preamble)

                    msg = ["python -c"]

                    #  imports
                    msg += [f"\"from {'.'.join(self.__class__.__module__.split('.')[:-1])} import {self.__class__.__name__};",
                            "from biohub.utils import EntityCreator;",
                            "from biohub.subject import Subject;"]

                    #  project
                    msg += [f"project = EntityCreator().createProject('tmp_{index}',",
                            f"'{self.entity.path.parent}',"
                            f"subjects =",
                            "[" + ", ".join([f"'{subject}'"for subject in subjects]) + "]);"]

                    #  process
                    msg += [f"{self.__class__.__name__}(entity = project, threads = {self.coresPerNode}, coresPerTask = {self.coresPerTask}).run()\""]

                    msg = " ".join(msg)

                    with open(f"{jobName}.slurm", "w") as slurm:
                        slurm.write(f"{preamble}\n\n{msg}")

                    self.runCommand(f"sbatch {jobName}.slurm")

def runFuction(subject,
               process,
               options,
               inputs,
               outputOutlines,
               processOutlines,
               extraAttrs):

    result = process.__class__(entity = subject,
                               threads = process.coresPerTask,
                               save = process.save,
                               duplicate = process.duplicate).run(options = options,
                                                                  inputs = inputs,
                                                                  outputOutlines = outputOutlines,
                                                                  processOutlines = processOutlines,
                                                                  **extraAttrs)
    return result
