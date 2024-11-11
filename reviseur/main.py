import time

from reviewer import Reviseur
from settings import Settings
from utils import initialize_logs

initialize_logs()


def main():
    while True:
        settings = Settings("param.xml")
        reviseur = Reviseur(settings)
        reviseur.workflow_banque_populaire()

        time.sleep(300)


if __name__ == "__main__":
    main()
