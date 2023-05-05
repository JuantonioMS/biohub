class Save:


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



    def _saveRecord(self,
                    process = None,
                    outputs: dict = {}) -> None:

        self.entity.addProcess(process)

        for output in outputs.values():

            self.entity.addFile(output.biohubFile)

        self.entity.save()

        process.entity = self.entity



    def _addDuration(self, process, date):

        process.duration = date - process.date

        return process