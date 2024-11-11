import re
import xml.etree.ElementTree as ET
from typing import Optional


class Settings:
    """
    Settings command class thre responsability
    to manage all the configuration imported from
    the param.xml
    """

    def __init__(self, xml_file):
        """This attributes will be loaded
        from the xml and stored in this
        class initilization attrs.

        Args:
            xml_file (str): path to xmlfile
        """
        self.xml_file = xml_file
        # Initialize attributes with types for autocomplete support
        self.default_browser: Optional[str] = None
        self.chrome_path: Optional[str] = None
        self.edge_path: Optional[str] = None
        self.firefox_path: Optional[str] = None
        self.set_auto_wait_timeout: Optional[int] = None
        self.start_icon: Optional[str] = None
        self.tout_accepter: Optional[str] = None
        self.trouver_une_agence: Optional[str] = None
        self.rue_type: Optional[str] = None
        self.code_postal: Optional[str] = None
        self.rechercher_click: Optional[str] = None
        self.lyon_perrache: Optional[str] = None
        self.cinq_agences_banque: Optional[str] = None
        self.quatre_quatre: Optional[str] = None
        self.quatre_detail: Optional[str] = None

        self.load_settings()

    def camel_to_snake(self, camel_str):
        """Simple convert camelCase to snake_case

        Args:
            camel_str (str): text in camelCase

        Returns:
            str: text in snake_case
        """
        snake_str = re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()
        return snake_str

    def load_settings(self):
        """
        Read and parse the XML description
        here we dynamically set the attrs
        converting their tag to the declared
        ones in the initialization of the class
        """
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()

            # Dynamically set attributes based on XML tags
            for elem in root.iter():
                tag = elem.tag
                text = elem.text

                tag = self.camel_to_snake(tag)

                if hasattr(self, tag):
                    value = int(text) if text.isdigit() else text
                    setattr(self, tag, value)
                else:
                    setattr(self, tag, text)

        except ET.ParseError as e:
            print(f"Error parsing XML file: {e}")
        except Exception as e:
            print(f"Error loading settings: {e}")
