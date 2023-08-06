import PrintDocx
import subprocess

stampante = subprocess.getoutput("lpstat -d").split(": ")
PrintDocx.PrintDocument("testo.docx",stampante[1])