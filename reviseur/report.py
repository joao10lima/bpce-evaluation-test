import logging
import os
import pathlib
from datetime import datetime

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


class Report:
    """Describes the generation of reports
    based on the screenshots save by the selenium
    driver. It must create a PDF in it describe
    all the steps until the error who blocked
    the continuation.
    """

    def __init__(self):
        """Initiates the report by creating the screenshot
        folder and setting the canvas to be worked upon.
        """
        datetime_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.image_dir = "screenshots/"
        pathlib.Path("reports/").mkdir(parents=True, exist_ok=True)
        self.output_pdf = f"reports/report_{datetime_now}.pdf"
        self.canvas = canvas.Canvas(self.output_pdf, pagesize=A4)
        self.title = f"{datetime_now}\nReport for banquepopulaire.fr"

    def generate_report(self, video_path):
        """Create the tiple page and add
        the images in order to PDF.

        Args:
            video_path (str): recorded video location
        """
        self.create_title_page(video_path)
        self.add_image_pages()
        self.canvas.save()
        logging.info(f"PDF saved: {self.output_pdf}")

    def create_title_page(self, video_path):
        """Creates the title page in the PDF
        report adding the path to the recorded
        video of the run.

        Args:
            video_path (str): Path to the execution video
        """
        self.canvas.setFont("Helvetica-Bold", 24)

        page_width, page_height = A4

        y_position = page_height / 2
        axis_mod = 0
        for title_text in self.title.split("\n"):
            text_width = stringWidth(title_text, "Helvetica-Bold", 24)
            x_position = (page_width - text_width) / 2
            self.canvas.drawString(
                x_position, y_position + axis_mod, title_text
            )
            axis_mod += 50

        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(
            x_position, y_position - 50, f"(Screen record: {video_path})"
        )
        self.canvas.showPage()

    def add_image_pages(self):
        """Loop over the screenshots taken
        on the reviewer process and join them
        in the PDF.
        """
        # Loop over images and add them to the report
        image_files = sorted(
            (
                entry
                for entry in os.scandir(self.image_dir)
                if entry.name.lower().endswith(".png")
            ),
            key=lambda entry: entry.stat().st_mtime,
        )

        for entry in image_files:
            self.add_image_page(entry.path)

    def sanitize_filename(self, filename):
        """Given that the filename for the
        snapshots generated in the reviewer
        tell the right steps that were taken
        we simply use them in a better format
        for visualization.

        Args:
            filename (str): path to file

        Returns:
            str: str
        """
        base_name = filename.rsplit(".", 1)[0]
        base_name = base_name.replace("_", " ")
        base_name = " ".join(
            [
                word.capitalize() if not word.isdigit() else word
                for word in base_name.split()
            ]
        )
        step_number = base_name.split(" ")[0]
        return f"Step {step_number} {base_name[len(step_number):].strip()}"

    def add_image_page(self, image_path):
        """Join any image from the steps taken
        and add to it a text that changes in case
        of error.

        Args:
            image_path (str): Screenshot to be added
        """
        screenshot = Image.open(image_path)
        aspect_ratio = screenshot.width / screenshot.height
        new_width = 400
        new_height = new_width / aspect_ratio

        self.canvas.drawImage(
            image_path, 25, 250, width=new_width, height=new_height
        )

        image_path = image_path.replace("screenshots/", "")
        if "FAILED" in image_path:
            self.canvas.setFont("Helvetica-Bold", 12)
            self.canvas.setFillColor(colors.red)
            sanitezed_name = self.sanitize_filename(image_path)
            text = f"FAILED - {sanitezed_name} - FOUND INCONSISTENT"
            self.canvas.drawString(30, 275 + new_height, text)
        else:
            self.canvas.setFont("Helvetica", 10)
            self.canvas.drawString(
                30, 275 + new_height, self.sanitize_filename(image_path)
            )
        self.canvas.showPage()
