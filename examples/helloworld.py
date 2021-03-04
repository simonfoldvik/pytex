"""Creates a hello world PDF and moves it to the desktop."""
from pytex import LaTeXDocument
with LaTeXDocument() as texdoc:
    texdoc.write("Hello World")
