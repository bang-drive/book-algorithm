import glob
import os
import random
import shutil

from absl import app, flags, logging


# Sample data from <data_dir>/<label> to <data_dir>/.sampling/<label>
flags.DEFINE_string('data_dir', None, 'Directory to load images.')
flags.mark_flag_as_required('data_dir')


def main(argv):
    os.chdir(flags.FLAGS.data_dir)
    shutil.rmtree('.sampling', ignore_errors=True)
    labels = [os.path.basename(label) for label in os.listdir('.') if os.path.isdir(label)]

    files = {}
    for label in labels:
        files[label] = glob.glob(F'{label}/**/*.jpg', recursive=True)
    sample_amount = min([len(files[label]) for label in files])

    for label in files:
        for file in random.sample(files[label], sample_amount):
            target_file = os.path.join('.sampling', file)
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            os.symlink(os.path.abspath(file), target_file)

    logging.info(F'Sampled {sample_amount} images from each label.')


if __name__ == '__main__':
    app.run(main)
