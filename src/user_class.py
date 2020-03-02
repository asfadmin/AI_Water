import os

from asf_hyp3 import API


class User:

    def __init__(self, mask_path: str, model_path: str, api: API):
        self.mask_path = mask_path
        self.model_path = model_path

        self._make_dirs(mask_path)
        self.api = api

    def _make_dirs(self) -> str:
        self.mask_path = os.path.join('mask', self.mask_path)
        if not os.path.isdir('mask'):
            os.mkdir('mask')
        if not os.path.isdir(self.mask_path):
            os.mkdir(self.mask_path)