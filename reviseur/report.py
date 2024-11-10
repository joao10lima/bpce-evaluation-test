import os
import pathlib
from datetime import datetime

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


class Report:
    def __init__(self):
        datetime_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.image_dir = "screenshots/"
        pathlib.Path("reports/").mkdir(parents=True, exist_ok=True)
        self.output_pdf = f"reports/report_{datetime_now}.pdf"
        self.canvas = canvas.Canvas(self.output_pdf, pagesize=A4)
        self.title = f"{datetime_now}\nReport for banquepopulaire.fr"

    def generate_report(self):
        self.create_title_page()
        self.add_image_pages()
        self.canvas.save()
        print(f"PDF saved: {self.output_pdf}")

    def create_title_page(self):
        self.canvas.setFont("Helvetica-Bold", 24)

        page_width, page_height = A4

        y_position = page_height / 2
        axis_mod = 0
        for title_text in self.title.split("\n"):
            text_width = stringWidth(title_text, "Helvetica-Bold", 24)
            x_position = (page_width - text_width) / 2
            self.canvas.drawString(x_position, y_position + axis_mod, title_text)
            axis_mod += 50
        self.canvas.showPage()

    def add_image_pages(self):
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

    def add_image_page(self, image_path):
        img = Image.open(image_path)
        aspect_ratio = img.width / img.height
        new_width = 400
        new_height = new_width / aspect_ratio

        self.canvas.drawImage(image_path, 50, 500, width=new_width, height=new_height)
        self.canvas.setFont("Helvetica", 16)
        self.canvas.drawString(
            50, 515 + new_height, f"Label: {os.path.basename(image_path)}"
        )
        self.canvas.showPage()
