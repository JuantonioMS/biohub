class Save:

    def _saveRecord(self,
                    process = None,
                    outputs: dict = {}) -> None:

        self.entity.addProcess(process)

        for output in outputs.values():

            self.entity.addFile(output.biohubFile)

        self.entity.save()

        process.entity = self.entity