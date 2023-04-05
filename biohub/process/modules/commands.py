import subprocess

from biohub.conf.general.constant import CONDA_ALIAS

class Commands:

    @property
    def biohubConda(self) -> str:

        alias = subprocess.run(f"/bin/bash -i -c alias -p",
                               shell = True,
                               executable = "/bin/bash",
                               capture_output= True).stdout.decode("UTF8").split("\n")

        try:
            return {element.split("=")[0].split(" ")[-1] : element.split("=")[-1].replace("'", "") for element in alias}[CONDA_ALIAS]
        except KeyError:
            return "/".join(subprocess.getoutput("which conda").split("/")[:-2]) + "/bin/conda"


    @property
    def biohubCondaShell(self) -> str:
        return "/".join(self.biohubConda.split("/")[:-2]) + "/etc/profile.d/conda.sh"


    def runCommand(self, *args, verbosity: bool = True) -> None:

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
        outputCode = output.returncode

        if verbosity and outputMsg:
            self.entity.logger.info(f"Process {self.id} :: COMMANDS :: Command -> " + command + "\n" + "Output -> " + outputMsg)

        if outputCode != 0:
            self.entity.logger.warning(f"Process {self.id} :: COMMANDS :: Return code is not 0 (code {outputCode})")

        return outputCode, outputMsg



    def runCondaPackage(self, *args, env: str = None, captureOutput: bool = True, verbosity: bool = True) -> None:

        """
        Ejecuta comandos recogidos en entornos conda de forma similar al método runCommand
        """

        self.entity.logger.info(f"Process {self.id} :: COMMANDS :: Running conda command")

        #  Búsqueda del shell de conda instalado en el sistema
        condaShell = "/".join(subprocess.getoutput("which conda").split("/")[:-2])

        if not env:
            env = self.environment

        #  Ruta completa a la shell de conda
        condaShell = f"{condaShell}/etc/profile.d/conda.sh"

        #condaShell = "/home/virtualvikings/.bhconda/etc/profile.d/conda.sh"

        # Montando la llamada al paquete junto a la inicializacion de la shell y el entorno
        command = ". " + " && ".join([f"{condaShell}",
                                      f"conda activate {env}",
                                      " ".join(args)])

        #commandLine = f"/home/virtualvikings/.bhconda/bin/conda run -n {env} {' '.join(args)}"

        outputCode, outputMsg = self.runCommand(command, verbosity = verbosity)

        return outputCode, outputMsg


    #  TODO
    def runSingularityPackage(self, *args):
        return ""

    #  TODO
    def runSystemPackage(self, *args):
        return ""