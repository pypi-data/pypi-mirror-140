import os
import subprocess
from docx2pdf import convert



def PrintDocument(filename, printer):

    inputFile = filename
    filename_pdf = filename.split(".")
    filename_pdf = filename_pdf[0]
    filename_pdf += ".pdf"

    outputFile = filename_pdf

    convert(inputFile, outputFile)

    print_cmd = 'lpr -P %s %s'
    os.system(print_cmd % (printer, filename_pdf))



