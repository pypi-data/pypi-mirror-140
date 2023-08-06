#!/bin/zsh
import tempfile
import subprocess
import shutil
import os
import pathlib

import jinja2

LATEX_PROCESSOR = "xelatex"

if not shutil.which(LATEX_PROCESSOR):
    raise Exception(f"{LATEX_PROCESSOR} is not installed in global path")


def tex_to_pdf(input_tex, extra_files=[], capture_output=True):
    with tempfile.TemporaryDirectory() as tmpdir:
        _, tmpfilename = tempfile.mkstemp(dir=tmpdir)
        latex_filename = f"{tmpfilename}.tex"
        for f in extra_files:
            f = pathlib.Path(f)
            shutil.copyfile(f, tmpdir / f)
        with open(latex_filename, "w") as latex_file:
            latex_file.write(input_tex)
        subprocess.run(
            [LATEX_PROCESSOR, latex_filename],
            capture_output=capture_output,
            check=True,
            cwd=tmpdir
        )
        pdf_filename = f"{tmpfilename}.pdf"
        with open(pdf_filename, "rb") as pdf_file:
            return pdf_file.read()


def render_latex(template_path, data):
    latex_jinja_env = jinja2.Environment(
        block_start_string=r"\BLOCK{", block_end_string="}",
        variable_start_string=r"\VAR{", variable_end_string="}",
        comment_start_string=r"\#{", comment_end_string="}",
        line_statement_prefix="%-",
        line_comment_prefix="%#",
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(os.path.abspath("."))
    )

    return latex_jinja_env.get_template(template_path).render(**data)
