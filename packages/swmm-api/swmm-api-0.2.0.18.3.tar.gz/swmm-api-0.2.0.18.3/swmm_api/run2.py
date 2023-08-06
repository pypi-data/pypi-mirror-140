from swmm_api.run import get_result_filenames
from .run_api import swmm5


def run(fn_inp):
    swmm5.run(fn_inp, *get_result_filenames(fn_inp))


def get_swmm_version():
    return '.'.join(swmm5.getVersion())
