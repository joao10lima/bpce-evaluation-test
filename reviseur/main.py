import os
import sys

from reviseur.utils import initialize_logs

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from reviseur.report import Report
from reviseur.reviewer import Reviseur
from reviseur.settings import Settings
from reviseur.video import Video

initialize_logs()


def main():
    settings = Settings("param.xml")

    video = Video()
    reviseur = Reviseur(settings, video)
    reviseur.workflow_banque_populaire()

    report = Report()
    report.generate_report()


if __name__ == "__main__":
    main()
