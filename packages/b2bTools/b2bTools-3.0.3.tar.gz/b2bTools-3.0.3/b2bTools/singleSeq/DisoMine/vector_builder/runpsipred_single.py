# -*- coding: utf-8 -*-
import os
import tempfile
import subprocess, sys

cwd = os.path.dirname(os.path.abspath(__file__))

DATADIR = cwd + '/psipred/data/'
# TEMPDIR = tempfile.mkdtemp() # cwd + '/psipred/tmp/'

if sys.platform == 'linux':
    SEQ2MTX = os.path.join(cwd, 'psipred/bin/linux/seq2mtx')
    PSIPRED = os.path.join(cwd, 'psipred/bin/linux/psipred')
    PSIPASS2 = os.path.join(cwd, 'psipred/bin/linux/psipass2')
elif sys.platform == 'darwin': # MacOS hosts
    SEQ2MTX = os.path.join(cwd, 'psipred/bin/osx/seq2mtx')
    PSIPRED = os.path.join(cwd, 'psipred/bin/osx/psipred')
    PSIPASS2 = os.path.join(cwd, 'psipred/bin/osx/psipass2')

for exec_path in [SEQ2MTX, PSIPRED, PSIPASS2]:
    if os.path.exists(exec_path):
        os.chmod(exec_path, int('777', 8))

def run(input, tmpfolder = None):
    if tmpfolder == None:
        tmpfolder = tempfile.mkdtemp()

    fasta = os.path.basename(input)
    name = fasta.split('.')[-2]

    mtx_filepath = os.path.join(tmpfolder, "{}.mtx".format(name))
    ss_filepath = os.path.join(tmpfolder, "{}.ss".format(name))
    ss2_filepath = os.path.join(tmpfolder, "{}.ss2".format(name))
    horiz_filepath = os.path.join(tmpfolder, "{}.horiz".format(name))

    # print('Psipred Running... processing: ' + name)

    with open(mtx_filepath, "w") as mtx_file:
        subprocess.run([SEQ2MTX, input], stdout=mtx_file)

    with open(ss_filepath, "w") as ss_file:
        subprocess.run( [PSIPRED, mtx_filepath, DATADIR + 'weights.dat', DATADIR + 'weights.dat2', DATADIR + 'weights.dat3'], stdout=ss_file)

    with open(horiz_filepath, "w") as horiz_file:
        subprocess.run( [PSIPASS2, DATADIR + 'weights_p2.dat', '1', '1.0', '1.0', ss2_filepath, ss_filepath], stdout=horiz_file)
