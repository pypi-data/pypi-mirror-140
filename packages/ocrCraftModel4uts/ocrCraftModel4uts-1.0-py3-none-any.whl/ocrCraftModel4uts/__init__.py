import os


def get_path():
    return os.path.realpath(__file__).split(os.path.basename(__file__))[0] + 'data/'
