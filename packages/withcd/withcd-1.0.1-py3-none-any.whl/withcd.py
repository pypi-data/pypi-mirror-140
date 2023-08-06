from os import chdir, getcwd

class cd:
    '''Change working directory utility compatible with with statements'''

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.origin = getcwd()
        chdir(self.path)

    def __exit__(self, *_):
        chdir(self.origin)
