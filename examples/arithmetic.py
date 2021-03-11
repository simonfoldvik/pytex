"""Creates a PDF with basic arithmetic
expressions and moves it to the desktop."""

from pytex  import LaTeXDocument
from random import randint

with LaTeXDocument(
    title="Basic Arithmetic",
    author="Python",
    documentclass="article",
    usepackages=["amsmath"],
    fontsize=12,
    ncompile=1) as texdoc:
    # Align basic arithmetic expressions.
    # Todo: add align method to class TeXFile.
    texdoc.write("Here is some basic arithmetic:")
    texdoc.write("\\begin{align*}")
    for _ in range(10):
        m = randint(1, 10)
        n = randint(1, 10)
        texdoc.write(f"{m} \\cdot {n} &= {m*n} \\\\")
    texdoc.write("\\end{align*}")
