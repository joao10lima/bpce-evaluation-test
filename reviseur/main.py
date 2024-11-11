import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from reviseur.reviewer import Reviseur
from reviseur.settings import Settings
from reviseur.utils import initialize_logs

initialize_logs()


def main():
    while True:
        settings = Settings("param.xml")
        reviseur = Reviseur(settings)
        reviseur.workflow_banque_populaire()

        time.sleep(300)


if __name__ == "__main__":
    main()
