import os
import sys
import logging
import time
import json
import mskaccess_operators.utilities as utils
try:
    import click
except ImportError as e:
    print(
        "fastq_to_bam: click is not installed, please install click as it is one of the requirements."
    )
    exit(1)
try:
    import click_log
except ImportError as e:
    print(
        "fastq_to_bam: click-log is not installed, please install click_log as it is one of the requirements."
    )
    exit(1)

"""
fastq_to_bam
~~~~~~~~~~~~~~~
:Description: console script for generating inputs for fastq_to_bam workflow
"""
"""
Created on November 15, 2019
Description: console script for generating inputs for fastq_to_bam workflow
@author: Ronak H Shah
"""

# Making logging possible
logger = logging.getLogger("mskaccess_operators")
click_log.basic_config(logger)
click_log.ColorFormatter.colors["info"] = dict(fg="green")
@click.group()
@click.option('-m', '--meta-information-json', required=False, type=click.Path(exists=True))
@click.option('-r', '--reference-json', required=False, default='../reference-json/fastq_to_bam_job.json', type=click.Path(exists=True))
@click_log.simple_verbosity_option(logger)
def cli():
    """Command that helps to generate inputs json for fastq_to_bam workflow for MSK-ACCESS."""
    logger_output = os.path.join("mskaccess_operators.log")
    fh = logging.FileHandler(logger_output)
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info("==================================================")
    logger.info(">>> Running fastq_to_bam input generation <<<")
    logger.info("==================================================")
    t1_start = time.perf_counter()
    t2_start = time.process_time()
    run()
    t1_stop = time.perf_counter()
    t2_stop = time.process_time()
    logger.info("--------------------------------------------------")
    logger.info("Elapsed time: %.1f [min]" % ((t1_stop - t1_start) / 60))
    logger.info("CPU process time: %.1f [min]" % ((t2_stop - t2_start) / 60))
    logger.info("--------------------------------------------------")

def run():
    pass                                                                                                                                                                                    
