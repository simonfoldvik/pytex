"""
pytex: a Python interface to writing LaTeX documents.
Supports automatic compilation and cleanup using context managers.

 Author: Simon Foldvik
Updated: 4 Mar 2021
"""

import os         as _os
import shutil     as _shutil
import tempfile   as _tempfile
import subprocess as _subprocess

# Todo: work out a better system to deal with options and packages,
#       perhaps defining appropriate classes? It should be possible
#       to merge instances of these classes to combine options and packages.

# Todo: support a better interface for compilation and moving the produced PDF
#       besides the automatic context manager.

# Default options to pass to the documentclass command.
DEFAULT_OPTIONS = [
    "a4paper",
    "oneside",
    "onecolumn",
    "notitlepage",
    "reqno",
    "UKenglish"
]

# Default packages to include in the LaTeX document.
# Todo: change "value" to "name" and correct this change in the rest of the code.
DEFAULT_PACKAGES = [
    {"value": "inputenc", "options": ["utf8"]},
    {"value": "fontenc", "options": ["T1"]},
    "textcomp",
    "lmodern",
    "microtype",
    "babel",
    "varioref",
    {"value": "hyperref", "options": ["pdftex"]},
    {"value": "cleveref", "options": ["capitalize", "nameinlink", "noabbrev"]}
]

def getdesktop():
    """Get path to the user's Desktop."""
    user = _os.getlogin()
    home = _os.path.join("/Users/", user) # macOS specific! Consider: _os.getenv("HOME").
    return _os.path.join(home, "Desktop")

def formatarg(arg):
    """
    Format the LaTeX argument for use in LaTeX documents,
    taking optional optional arguments into account.

    Parameters
    ----------
        arg: str, or dict of type {"value": str, "options": [str, str, ...]}

    Examples
    --------
        str  -> "{str}"
        dict -> "[option, option, ...]{value}".format(dict.options, dict.value)
    """
    if isinstance(arg, dict):
        return "[%s]{%s}" % (", ".join(arg["options"]), arg["value"])
    return "{%s}" % arg

class TeXFile:
    """
    Wrapper for a file object pointing to
    a (La)TeX file, providing convenience
    methods for writing LaTeX commands.
    """
    def __init__(self, texfile):
        """
        Parameters
        ----------
            texfile: file pointer to (open) (La)TeX file
        """
        self._texfile = texfile

    def closed(self):
        """Returns True iff the underlying TeX file is closed."""
        return self._texfile.closed

    def documentclass(self, documentclass, options=[]):
        """Add a documentclass command (with options) to the TeX file."""
        # Todo: make use of formatarg?
        if options:
            optstr = ", ".join(options)
            self._texfile.write("\\documentclass[%s]{%s}\n" % (optstr, documentclass))
        else:
            self._texfile.write("\\documentclass{%s}\n" % documentclass)

    def beginDocument(self):
        """Add a beginDocument command to the TeX file."""
        self._texfile.write("\\begin{document}\n")
    
    def endDocument(self):
        """Add an endDocument command to the TeX file."""
        self._texfile.write("\\end{document}\n")

    def author(self, author):
        """Add an author field command to the TeX file."""
        self._texfile.write("\\author{%s}\n" % author)

    def title(self, title):
        """Add a title field command to the TeX file."""
        self._texfile.write("\\title{}\n".format(formatarg(title)))

    def maketitle(self):
        """Add a maketitle command to the TeX file."""
        self._texfile.write("\\maketitle\n")

    def newpage(self):
        """Add a newpage command to the TeX file."""
        self._texfile.write("\\newpage\n")

    def clearpage(self):
        """Add a clearpage command to the TeX file."""
        self._texfile.write("\\clearpage\n")

    def usepackage(self, pkg):
        """Add a usepackage command to the TeX file."""
        self._texfile.write("\\usepackage{}\n".format(formatarg(pkg)))

    def usepackages(self, pkgs):
        """Add a usepackage command to the TeX file, one for each argument."""
        self._texfile.writelines("\\usepackage{}\n".format(formatarg(pkg)) for pkg in pkgs)

    def write(self, line, end='\n'):
        """
        Write to the TeX file.
        Automatically appends a newline character.
        """
        self._texfile.write("{}{}".format(line, end))

    def writelines(self, lines, end='\n'):
        """
        Write lines to TeX file.
        Automatically appends newline characters.
        """
        self._texfile.writelines("{}{}".format(line, end) for line in lines)

    def display(self, math):
        """Add math in display style to the TeX file."""
        display = "\\[ {} \\]\n".format(math)
        self._texfile.write(display)

    def equation(self, math, label=None, tag=None, numbered=True):
        """
        Add an equation environment to the TeX file.

        Parameters
        ----------
                math: contents to display
               label: optional label for the equation environment
                 tag: optional tag for naming the equation reference
            numbered: whether or not to add an equation number
        """
        if numbered:
            self._texfile.write("\\begin{equation}\n")
            if label:
                self._texfile.write("\\label{%s}\n" % label)
                if tag:
                    self._texfile.write("\\tag{%s}\n" % tag)
            self._texfile.write("{}\n".format(math))
            self._texfile.write("\\end{equation}\n")
        else:
            self._texfile.write("\\begin{equation*}\n")
            if label:
                self._texfile.write("\\label{%s}\n" % label)
            self._texfile.write("{}\n".format(math))
            self._texfile.write("\\end{equation*}\n")

    def quote(self, *lines):
        """Add a quote environment to the TeX file."""
        self._texfile.write("\\begin{quote}\n")
        self._texfile.writelines("{}\n".format(line) for line in lines)
        self._texfile.write("\\end{quote}\n")

    def quotation(self, *lines):
        """Add a quotation environment to TeX file."""
        self._texfile.write("\\begin{quotation}\n")
        self._texfile.writelines("{}\n".format(line) for line in lines)
        self._texfile.write("\\end{quotation}\n")

    def figure(self):
        """Add a figure to the TeX file."""
        raise NotImplementedError("Figure this out")

    def tabular(self):
        """Add a table to the TeX file."""
        raise NotImplementedError("Figure this out")

    def input(self, name):
        """Add an input file command to the TeX file."""
        self._texfile.write("\\input{%s}\n" % name)

    def include(self, name):
        """Add an include file command to the TeX file."""
        self._texfile.write("\\include{%s}\n" % name)

    def includeonly(self, names):
        """Add an includeonly file command to the TeX file."""
        raise NotImplementedError("includeonly not yet implemented")

    def tableofcontents(self):
        """Add a tableofcontents command to the TeX file."""
        self._texfile.write("\\tableofcontents\n")

    def printbibliography(self):
        """Add a printbibliography command to the TeX file."""
        self._texfile.write("\\printbibliography\n")

class LaTeXDocument:
    """
    LaTeX document wrapper.

    Contains the settings of the LaTeX document, and methods for
    writing the preamble, compiling the document, and moving the
    compiled PDF to a designated location.
    """
    def __init__(self,
        title=None,
        author=None,
        documentclass="amsart",
        options=DEFAULT_OPTIONS,
        usepackages=DEFAULT_PACKAGES,
        preamble=[],
        fontsize=11,
        columns=1,
        fullpage=False,
        ncompile=2,
        dst=None,
        overwrite=False):
        """
        Store settings for the configuration of the LaTeX document.
        +-----------------+------------------------------------------+
        |  Parameters     |  Description                             |
        +-----------------+------------------------------------------+
        |  title          |  document title                          |
        |  author         |  document author(s)                      |
        +-----------------+------------------------------------------+
        |  documentclass  |  LaTeX document class                    |
        |  options        |  documentclass options                   |
        |  usepackages    |  packages to include in the preamble     |
        |  preamble       |  lines to include in the preamble        |
        |  fontsize       |  PDF fontsize (10-12)                    |
        |  columns        |  1 or 2 (onecolumn or twocolumn)         |
        |  fullpage       |  use fullpage package?                   |
        +-----------------+------------------------------------------+
        |  ncompile       |  number of pdflatex compilations         |
        |  dst            |  output destination (file or directory)  |
        |  overwrite      |  overwrite policy (bool)                 |
        +-----------------+------------------------------------------+
        """
        # Required.
        self.title = title
        self.author = author

        # LaTeX configuration.
        self.documentclass = documentclass
        self.options = options
        self.usepackages = usepackages
        self.preamble = preamble
        self.fontsize = fontsize
        self.columns = columns
        self.fullpage = fullpage

        # Compilation.
        self.ncompile = ncompile
        self.dst = dst
        self.overwrite = overwrite

    def _parseoptions(self):
        """Obtain options to provide to the documentclass command."""
        # Remove fontsize and column options; use the provided ones instead.
        for opt in ("10pt", "11pt", "12pt", "onecolumn", "twocolumn"):
            if opt in self.options:
                self.options.remove(opt)
        self.options.append("{}pt".format(self.fontsize))
        if self.columns == 1:
            self.options.append("onecolumn")
        elif self.columns == 2:
            self.options.append("twocolumn")
        else:
            raise ValueError("Unrecognized column specifier: {}".format(self.columns))
        return self.options

    def _writepreamble(self):
        """Write the preamble to the texfile."""
        docopts = self._parseoptions()
        self._texfile.documentclass(self.documentclass, docopts)
        if self.fullpage and ("fullpage" not in self.usepackages):
            # Todo: check for conflicting "fullpage" in usepackages and fullpage=False.
            self.usepackages.insert(0, "fullpage")
        self._texfile.usepackages(self.usepackages)
        self._texfile.writelines(self.preamble)
        if self.title:
            self._texfile.title(self.title)
        if self.author:
            self._texfile.author(self.author)
        self._texfile.beginDocument()
        if self.title:
            self._texfile.maketitle()

    def _compilepdf(self):
        """Compile the TeX file the specified number of times."""
        # Todo: chdir back to where we were after compilation?
        _os.chdir(self._tmpdir.name)
        for _ in range(self.ncompile):
            _subprocess.call(["pdflatex", self._mainfile.name])

    def _movepdf(self):
        """Move the PDF file to the desired location."""
        # Todo: this is a horribly complicated function: break into parts?
        if self.dst:
            # Output destination provided.
            if _os.path.isdir(self.dst):
                # Directory provided.
                # Move PDF file there without changing its name.
                pdfname = _os.path.basename(self._mainfile.name).replace(".tex", ".pdf")
                outpath = _os.path.join(self.dst, pdfname)
                if _os.path.isfile(outpath) and not self.overwrite:
                    # The file already exists,
                    # and we are told not to overwrite: abort!
                    raise IOError("{} already exists, instructed not to overwrite".format(outpath))
                # Todo: Consider race conditions with the above existence check?
                _shutil.move(pdfname, outpath)
            elif _os.path.isfile(self.dst):
                # We are given an existent file path. Overwrite?
                if self.overwrite:
                    # Q: Should we ensure the output has .pdf extension? Warn if not?
                    _shutil.move(self._mainfile.name.replace(".tex", ".pdf"), self.dst)
                else:
                    raise IOError("{} already exists, instructed not to overwrite".format(self.dst))
            else:
                # We are not given a directory or an existing file path.
                # Simply move the PDF file there.
                # _shutil.move should handle the case of a nonexistent basedir.
                _shutil.move(self._mainfile.name.replace(".tex", ".pdf"), self.dst)
        else:
            # Output destination not provided.
            # Assume Desktop.
            desktop = getdesktop()
            pdfname = _os.path.basename(self._mainfile.name).replace(".tex", ".pdf")
            outpath = _os.path.join(desktop, pdfname)
            if _os.path.isfile(outpath) and not self.overwrite:
                # The file already exists,
                # and we are told not to overwrite: abort!
                raise IOError("{} already exists, instructed not to overwrite".format(outpath))
            _shutil.move(pdfname, outpath)

    def __enter__(self):
        self._tmpdir = _tempfile.TemporaryDirectory()
        self._mainfile = _tempfile.NamedTemporaryFile(
            mode='w',
            dir=self._tmpdir.name,
            prefix="pytex_",
            suffix=".tex",
            delete=False # Containing dir self-destructs.
        )
        self._texfile = TeXFile(self._mainfile.file)
        self._writepreamble()
        return self._texfile

    def __exit__(self, exc, val, tb):
        """Close files, compile document, move PDF, and perform cleanup."""
        self._texfile.endDocument()
        self._mainfile.file.close()
        self._compilepdf()
        self._movepdf()
        self._tmpdir.cleanup()
