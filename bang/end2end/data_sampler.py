import glob
import os
import pprint
import random
import shutil

from absl import app, flags, logging

from bang.end2end.common import count_subdir_files


# Sample data from <data_dir>/<label> to <data_dir>/../sampled/<label>
flags.DEFINE_string('data_dir', None, 'Directory to load images.')
flags.mark_flag_as_required('data_dir')

SAMPLE_FACTOR = {
    '0_STRAIGHT': 0.6,
}


def main(argv):
    recorded = count_subdir_files(flags.FLAGS.data_dir)
    logging.info('Recorded:')
    pprint.pprint(recorded)

    os.chdir(flags.FLAGS.data_dir)
    target_path = os.path.abspath('../sampled')

    shutil.rmtree(target_path, ignore_errors=True)
    labels = [os.path.basename(label) for label in os.listdir('.') if os.path.isdir(label)]

    files = {}
    for label in labels:
        files[label] = glob.glob(F'{label}/**/*.jpg', recursive=True)
    sample_amount = min([len(files[label]) for label in files])

    for label in files:
        to_sample = int(sample_amount * SAMPLE_FACTOR.get(label, 1))
        sampled = files[label]
        if to_sample < len(files[label]):
            sampled = random.sample(files[label], to_sample)
        for file in sampled:
            target_file = os.path.join(target_path, file)
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            os.symlink(os.path.abspath(file), target_file)

    sampled = count_subdir_files(target_path)
    logging.info('Sampled:')
    pprint.pprint(sampled)


if __name__ == '__main__':
    app.run(main)
