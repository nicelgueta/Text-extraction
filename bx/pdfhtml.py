
##########################
# PDF CONVERSION ENGINES FOR USE BY THE SOUP OBJECT
##########################

# also support cmd utility
import os
import subprocess

def pdf2htmlEX(pdf_file_path: str, dest: str) -> str: 
    """
    Returns HTML filepath of converted PDF
    """
    assert os.path.exists(pdf_file_path), f'path: {pdf_file_path} is not valid'
    assert os.path.isdir(dest), f'path: {dest} is not a valid directory'
    bx_dir = os.path.dirname(__file__)
    pdf_exe = os.path.join(bx_dir,'tp','pdf2htmlEX','pdf2htmlEX.exe')
    cmd = f'{pdf_exe} {pdf_file_path} --dest-dir {dest}'
    print(pdf_exe)
    subprocess.Popen(cmd).wait()
    html_filename = pdf_file_path.split('\\')[-1].replace('pdf','html')
    return os.path.join(dest,html_filename)

def msword(pdf_file_path: str, dest: str):
    pass
