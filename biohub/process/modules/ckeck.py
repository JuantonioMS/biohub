from pathlib import Path

class Check:

    def _checkStatus(self, process = None, outputs: dict = {}) -> bool:

        for output in outputs.values():

            if not Path(output.path).exists(): return False

        return True