import collections
import glob
import os


def count_subdir_files(path):
    result = collections.defaultdict(int)
    if os.path.exists(path):
        for label in os.listdir(path):
            subdir = os.path.join(path, label)
            if os.path.isdir(subdir):
                for f in glob.glob(F'{subdir}/**', recursive=True):
                    if os.path.isfile(f):
                        result[label] += 1
    return result
