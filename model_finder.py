'''
Script to help choose best model visually
For 1 vh vv pair
Predict mask for every model in models
'''

import os
import subprocess
from tkinter import *
from tkinter.filedialog import askopenfilename
from pathlib import Path


def getFileName():
    root = Tk()
    filename = askopenfilename()
    root.destroy()
    return filename


def main():
    # get inputs
    model_path = 'models/ai_test_5'
    script = 'create_mask.py'
    print('select vv from gui')
    vv_path = getFileName()
    print('select vh from gui')
    vh_path = getFileName()

    # mkdir
    all_models_path = f'{Path(vv_path).stem}_all_models')
    if os.path.exists(all_models_path):
        shutil.rmtree(all_models_path)
    os.mkdir(all_models_path)

    # make masks
    for model in os.listdir(model_path):
        out_path=os.path.join('all_models_path', f'mask_{model[:-3]}.tif')
        subprocess.call(
            f"python3 create_mask.py \
            {os.path.join(model_path, model)} \
            {vv_path} \
            {vh_path} \
            {out_path}",
            shell=True
        )


if __name__=='__main__':
    main()
