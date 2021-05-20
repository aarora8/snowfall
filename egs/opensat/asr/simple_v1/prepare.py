#!/usr/bin/env python3

# Copyright (c)  2020  Xiaomi Corporation (authors: Junbo Zhang, Haowen Qiu)
# Apache 2.0
import argparse
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from collections import defaultdict

import torch
import lhotse
from lhotse.utils import fastcopy
from lhotse import CutSet, Fbank, FbankConfig, LilcomHdf5Writer, combine
from lhotse.recipes import prepare_librispeech, prepare_safet, prepare_musan
from lhotse import validate_recordings_and_supervisions
from lhotse.audio import Recording, RecordingSet
from lhotse.supervision import SupervisionSegment, SupervisionSet
from lhotse.utils import Pathlike, check_and_rglob, recursion_limit
from snowfall.common import str2bool

# Torch's multithreaded behavior needs to be disabled or it wastes a lot of CPU and
# slow things down.  Do this outside of main() in case it needs to take effect
# even when we are not invoking the main (e.g. when spawning subprocesses).
torch.set_num_threads(1)
torch.set_num_interop_threads(1)


@contextmanager
def get_executor():
    # We'll either return a process pool or a distributed worker pool.
    # Note that this has to be a context manager because we might use multiple
    # context manager ("with" clauses) inside, and this way everything will
    # free up the resources at the right time.
    try:
        # If this is executed on the CLSP grid, we will try to use the
        # Grid Engine to distribute the tasks.
        # Other clusters can also benefit from that, provided a cluster-specific wrapper.
        # (see https://github.com/pzelasko/plz for reference)
        #
        # The following must be installed:
        # $ pip install dask distributed
        # $ pip install git+https://github.com/pzelasko/plz
        name = subprocess.check_output('hostname -f', shell=True, text=True)
        if name.strip().endswith('.clsp.jhu.edu'):
            import plz
            from distributed import Client
            with plz.setup_cluster() as cluster:
                cluster.scale(80)
                yield Client(cluster)
            return
    except:
        pass
    # No need to return anything - compute_and_store_features
    # will just instantiate the pool itself.
    yield None


def locate_corpus(*corpus_dirs):
    for d in corpus_dirs:
        if os.path.exists(d):
            return d
    print("Please create a place on your system to put the downloaded Librispeech data "
          "and add it to `corpus_dirs`")
    sys.exit(1)


def get_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--num-jobs',
        type=int,
        default=min(15, os.cpu_count()),
        help='When enabled, use 960h LibriSpeech.')
    return parser


def main():
    args = get_parser().parse_args()
    musan_dir = locate_corpus(
        Path('/export/corpora5/JHU/musan'),
        Path('/export/common/data/corpora/MUSAN/musan'),
        Path('/root/fangjun/data/musan'),
    )

    output_dir = Path('exp/data')
    print('safet manifest preparation:')
    safet_manifests = prepare_safet(
        corpus_dir='/exp/aarora/corpora/safet/',
        lexicon_dir='data/local/dict_nosp/lexicon/',
        output_dir=output_dir
    )

    print('ami manifest preparation:')
    ami_manifests = defaultdict(dict)
    recording_set_dev, supervision_set_dev = lhotse.kaldi.load_kaldi_data_dir('/exp/aarora/archive/snowfall/ami/kaldi_data/dev', 16000)
    validate_recordings_and_supervisions(recording_set_dev, supervision_set_dev)
    supervision_set_dev.to_json(output_dir / f'supervisions_dev.json')
    ami_manifests['dev'] = {
                'recordings': recording_set_dev,
                'supervisions': supervision_set_dev
            }

    recording_set_eval, supervision_set_eval = lhotse.kaldi.load_kaldi_data_dir('/exp/aarora/archive/snowfall/ami/kaldi_data/eval', 16000)
    validate_recordings_and_supervisions(recording_set_eval, supervision_set_eval)
    supervision_set_eval.to_json(output_dir / f'supervisions_eval.json')
    ami_manifests['eval'] = {
                'recordings': recording_set_eval,
                'supervisions': supervision_set_eval
            }

    recording_set_train, supervision_set_train = lhotse.kaldi.load_kaldi_data_dir('/exp/aarora/archive/snowfall/ami/kaldi_data/train', 16000)
    validate_recordings_and_supervisions(recording_set_train, supervision_set_train)
    supervision_set_eval.to_json(output_dir / f'supervisions_train.json')
    ami_manifests['train'] = {
                'recordings': recording_set_train,
                'supervisions': supervision_set_train
            }

    print('icsi manifest preparation:')
    icsi_manifests = defaultdict(dict)
    recording_set_dev, supervision_set_dev = lhotse.kaldi.load_kaldi_data_dir('/home/hltcoe/aarora/kaldi/egs/icsi/s5/data/ihm/dev_fixed2', 16000)
    validate_recordings_and_supervisions(recording_set_dev, supervision_set_dev)
    supervision_set_dev.to_json(output_dir / f'supervisions_dev.json')
    icsi_manifests['dev'] = {
                'recordings': recording_set_dev,
                'supervisions': supervision_set_dev
            }

    recording_set_eval, supervision_set_eval = lhotse.kaldi.load_kaldi_data_dir('/home/hltcoe/aarora/kaldi/egs/icsi/s5/data/ihm/eval_fixed2', 16000)
    validate_recordings_and_supervisions(recording_set_eval, supervision_set_eval)
    supervision_set_eval.to_json(output_dir / f'supervisions_eval.json')
    icsi_manifests['eval'] = {
                'recordings': recording_set_eval,
                'supervisions': supervision_set_eval
            }

    recording_set_train, supervision_set_train = lhotse.kaldi.load_kaldi_data_dir('/home/hltcoe/aarora/kaldi/egs/icsi/s5/data/ihm/train_cleaned_fixed2', 16000)
    validate_recordings_and_supervisions(recording_set_train, supervision_set_train)
    supervision_set_eval.to_json(output_dir / f'supervisions_train.json')
    icsi_manifests['train'] = {
                'recordings': recording_set_train,
                'supervisions': supervision_set_train
            }

    print('Musan manifest preparation:')
    musan_cuts_path = output_dir / 'cuts_musan.json.gz'
    musan_manifests = prepare_musan(
        corpus_dir=musan_dir,
        output_dir=output_dir,
        parts=('music', 'speech', 'noise')
    )

    print('Feature extraction:')
    extractor = Fbank(FbankConfig(num_mel_bins=80))
    with get_executor() as ex:  # Initialize the executor only once.
        for partition, manifests in safet_manifests.items():
            if (output_dir / f'cuts_safet_{partition}.json.gz').is_file():
                print(f'{partition} already exists - skipping.')
                continue
            print('Processing', partition)
            cut_set = CutSet.from_manifests(
                recordings=manifests['recordings'],
                supervisions=manifests['supervisions']
            )
            cut_set = cut_set.trim_to_supervisions()
            if 'train' in partition:
                cut_set = cut_set + cut_set.perturb_speed(0.9) + cut_set.perturb_speed(1.1)
            cut_set = cut_set.compute_and_store_features(
                extractor=extractor,
                storage_path=f'{output_dir}/feats_safet_{partition}',
                num_jobs=args.num_jobs if ex is None else 80,
                executor=ex,
                storage_type=LilcomHdf5Writer
            )
            safet_manifests[partition]['cuts'] = cut_set
            cut_set.to_json(output_dir / f'cuts_safet_{partition}.json.gz')

        for partition, manifests in ami_manifests.items():
            print(f"Processing {partition} ")
            if (output_dir / f'cuts_icsi_{partition}.json.gz').is_file():
                print(f'{partition} already exists - skipping.')
                continue
            cut_set = CutSet.from_manifests(
                recordings=manifests['recordings'],
                supervisions=manifests['supervisions']
            )
            cut_set = cut_set.trim_to_supervisions()
            cut_set = cut_set.map(lambda c: fastcopy(c, supervisions=[s for s in c.supervisions if s.start == 0 and abs(s.duration - c.duration) <= 1e-3]))
            if 'train' in partition:
                cut_set = cut_set + cut_set.perturb_speed(0.9) + cut_set.perturb_speed(1.1)

            print(f"store cutset supervision")
            cut_set = cut_set.compute_and_store_features(
                extractor=extractor,
                storage_path=f'{output_dir}/feats_icsi_{partition}',
                # when an executor is specified, make more partitions
                num_jobs=args.num_jobs if ex is None else 80,
                executor=ex,
                storage_type=LilcomHdf5Writer
            )
            ami_manifests[partition]['cuts'] = cut_set
            cut_set.to_json(output_dir / f'cuts_icsi_{partition}.json.gz')


        for partition, manifests in icsi_manifests.items():
            print(f"Processing {partition} ")
            if (output_dir / f'cuts_icsi_{partition}.json.gz').is_file():
                print(f'{partition} already exists - skipping.')
                continue
            cut_set = CutSet.from_manifests(
                recordings=manifests['recordings'],
                supervisions=manifests['supervisions']
            )
            cut_set = cut_set.trim_to_supervisions()
            cut_set = cut_set.map(lambda c: fastcopy(c, supervisions=[s for s in c.supervisions if s.start == 0 and abs(s.duration - c.duration) <= 1e-3]))
            if 'train' in partition:
                cut_set = cut_set + cut_set.perturb_speed(0.9) + cut_set.perturb_speed(1.1)

            print(f"store cutset supervision")
            cut_set = cut_set.compute_and_store_features(
                extractor=extractor,
                storage_path=f'{output_dir}/feats_icsi_{partition}',
                # when an executor is specified, make more partitions
                num_jobs=args.num_jobs if ex is None else 80,
                executor=ex,
                storage_type=LilcomHdf5Writer
            )
            icsi_manifests[partition]['cuts'] = cut_set
            cut_set.to_json(output_dir / f'cuts_icsi_{partition}.json.gz')

        # Now onto Musan
        if not musan_cuts_path.is_file():
            print('Extracting features for Musan')
            # create chunks of Musan with duration 5 - 10 seconds
            musan_cuts = CutSet.from_manifests(
                recordings=combine(part['recordings'] for part in musan_manifests.values())
            ).cut_into_windows(10.0).filter(lambda c: c.duration > 5).compute_and_store_features(
                extractor=extractor,
                storage_path=f'{output_dir}/feats_musan',
                num_jobs=args.num_jobs if ex is None else 80,
                executor=ex,
                storage_type=LilcomHdf5Writer
            )
            musan_cuts.to_json(musan_cuts_path)


if __name__ == '__main__':
    main()
