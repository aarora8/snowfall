#!/usr/bin/env python3

# Copyright (c)  2020  Xiaomi Corporation (authors: Junbo Zhang, Haowen Qiu)
# Apache 2.0
import argparse
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import torch
from lhotse import CutSet, Fbank, FbankConfig, LilcomHdf5Writer, combine
from lhotse.recipes import prepare_librispeech, prepare_safet, prepare_musan

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
    output_dir = Path('exp/data')
    print('safet manifest preparation:')
    safet_manifests = prepare_safet(
        corpus_dir='/exp/aarora/corpora/safet/',
        lexicon_dir='data/local/dict_nosp/lexicon/',
        output_dir=output_dir
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



if __name__ == '__main__':
    main()
