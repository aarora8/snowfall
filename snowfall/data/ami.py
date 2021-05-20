import logging
from functools import lru_cache

from lhotse import CutSet, load_manifest
from snowfall.data.asr_datamodule import AsrDataModule


class AmiAsrDataModule(AsrDataModule):
    """
    Aishell ASR data module.
    """
    @lru_cache()
    def train_cuts(self) -> CutSet:
        logging.info("About to get train cuts")
        return load_manifest(self.args.feature_dir / 'cuts_ami_train.json.gz')

    @lru_cache()
    def valid_cuts(self) -> CutSet:
        logging.info("About to get valid cuts")
        return load_manifest(self.args.feature_dir / 'cuts_ami_dev.json.gz')

    @lru_cache()
    def test_cuts(self) -> CutSet:
        logging.info("About to get test cuts")
        return load_manifest(self.args.feature_dir / 'cuts_ami_eval.json.gz')


