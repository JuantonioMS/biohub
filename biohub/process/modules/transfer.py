class Transfer:

    def _moveFiles(self,
                   outputs: dict) -> None:

        self._transferTemporalFiles(outputs)

        self._deleteTemporalDirectory()


    def _transferTemporalFiles(self, outputs: dict) -> None:

        for output in outputs.values():

            self.runCommand(f"mv",
                            f"{output.temporal}",
                            f"{output.path}")


    def _deleteTemporalDirectory(self) -> None:

        self.runCommand(f"rm -rf {self.temporalDirectory}")