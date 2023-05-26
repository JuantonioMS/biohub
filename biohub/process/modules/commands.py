import subprocess

from pathlib import Path

class Commands:


    #%%  GENERAL COMMAND SECTION________________________________________________________________________________________


    def runCommand(self, *args,
                   verbosity: bool = True) -> tuple:

        """
        Ejecuta comandos del sistema. Retorna el valor de ejecución resultante. Suele ser 0 el valor de todo correcto.
        Tiene la opción de capturar la salida si captureOuput es True y retorna el output.
        """

        command = " ".join(args)

        output = subprocess.run(command,
                                shell = True,
                                executable = "/bin/bash",
                                capture_output = True)

        outputMsg = (output.stdout.decode("UTF8") + "\n" + output.stderr.decode("UTF8")).strip("\n")
        outputCode = int(output.returncode)

        if verbosity:

            if not outputMsg: outputMsg = "No output"

            self.logger.info(f"Process {self.id} :: COMMANDS :: Command -> " + command +
                                    "\n" +
                                    "Output -> " + outputMsg)

        if outputCode != 0:
            self.logger.warning(f"Process {self.id} :: COMMANDS :: Return code is not 0 (code {outputCode})")

        return outputCode, outputMsg


    #%%  CONDA SECTION__________________________________________________________________________________________________


    @property
    def condaPath(self) -> Path:

        """Return conda folder path, if it is not possible raise an error"""

        try:
            return Path("/".join(subprocess.getoutput("which conda").split("/")[:-2]))

        except:
            self.logger.error(f"Process {self.id} :: COMMANDS :: No Anaconda/Miniconda found")
            raise ProcessLookupError("No Anaconda/Miniconda installation found, please install. If it is installed " +
                                     "check $PATH")


    @property
    def condaApp(self) -> Path:

        """Return conda bin executable path"""

        return Path(self.condaPath, "bin/conda")


    @property
    def condaShell(self) -> Path:

        """Return conda shell path """

        return Path(self.condaPath, "etc/profile.d/conda.sh")



    def runCondaPackage(self, *args,
                        environment: str = None,
                        prefix: str = ".",
                        verbosity: bool = True) -> tuple:

        """
        Ejecuta comandos recogidos en entornos conda de forma similar al método runCommand
        """

        self.logger.info(f"Process {self.id} :: COMMANDS :: Running conda command")

        if not environment:
            environment = self.environment

        return self.runCommand(prefix, f"{self.condaShell} && conda activate {environment} && ", *args,
                               verbosity = verbosity)


    #%%  SINGULARITY SECTION____________________________________________________________________________________________


    #  TODO
    def runSingularityPackage(self):
        pass


    #%%  SYSTEM SECTION_________________________________________________________________________________________________


    #  TODO
    def runSystemPackage(self):
        pass