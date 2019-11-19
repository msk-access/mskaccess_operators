import os
import sys
import logging
import time
import json
import pathlib
from addict import Dict
from pprint import pprint
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
BASE_DIR = pathlib.Path('__file__').resolve().parent
# Making logging possible
logger = logging.getLogger("mskaccess_operators")
click_log.basic_config(logger)
click_log.ColorFormatter.colors["info"] = dict(fg="green")
@click.group()


def cli():
    """ Sub-commands for fastq_to_bam input generation"""
    pass

@cli.command()
@click.option('-m', '--meta-information-json', type=click.Path(exists=True))
@click.option('-r', '--reference-json', default=BASE_DIR.joinpath("reference-json", "fastq_to_bam_job.json"), type=click.Path(exists=True))
@click_log.simple_verbosity_option(logger)

def generate(meta_information_json,reference_json):
    """Command that helps to generate inputs json for fastq_to_bam workflow for MSK-ACCESS."""
    logger_output = pathlib.Path.cwd().joinpath("mskaccess_operators.log")
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
    print(meta_information_json, "\n")
    read_json(meta_information_json)
    print(reference_json, "\n")
    t1_stop = time.perf_counter()
    t2_stop = time.process_time()
    logger.info("--------------------------------------------------")
    logger.info("Elapsed time: %.1f [min]" % ((t1_stop - t1_start) / 60))
    logger.info("CPU process time: %.1f [min]" % ((t2_stop - t2_start) / 60))
    logger.info("--------------------------------------------------")
    return 

def read_json(json_file):
    """ Given a json file, read it and store content for each sample."""
    json_dict = Dict()
    with open(json_file, 'r') as f:
        json_dict = Dict(json.load(f))
    generate_results(json_dict.results)
def generate_results(results):
    CN = "MSKCC"
    PL = "Illumina"

    samples = dict()

    for i,v in enumerate(results):
        meta = v['metadata']
        libraries = meta['libraries']
        runs = libraries['runs']
        bid = v['id']
        fpath = v['path']
        fname = v['file_name']
        igo_id = meta['igoId']
        lb = libraries['libraryIgoId']
        bait_set = meta['baitSet']
        tumor_type = meta['tumorOrNormal']
        species = meta['species']
        cmo_sample_name = meta['cmoSampleName']
        flowcell_id = runs['flowCellId']
        barcode_index = libraries['barcodeIndex']
        cmo_patient_id = meta['cmoPatientId']
        pu = flowcell_id
        run_date = runs['runDate']
        if barcode_index:
            pu = '_'.join([flowcell_id,  barcode_index])
        rg_id = pu + "_1"
        if cmo_sample_name:
            rg_id = '_'.join([cmo_sample_name, pu])
        else:
            print("cmoSampleName is None for %s; using PU as read group ID instead." % lb)
        
        if rg_id not in samples:
            samples[rg_id] = dict()
            sample = dict()
            sample['read_group_sequnecing_center'] = (CN)
            sample['read_group_sequencing_platform'] = (PL)
            sample['read_group_platform_unit'] = (pu)
            sample['read_group_library'] = (lb)
            sample['tumor_type'] = (tumor_type)
            sample['read_group_identifier'] = (rg_id)
            sample['read_group_sample_name'] = (cmo_sample_name)
            sample['species'] = (species)
            sample['patient_id'] = cmo_patient_id
            sample['bait_set'] = bait_set
            sample['igo_id'] = igo_id
            sample['run_date'] = run_date
        else:
            sample = samples[rg_id]
        
        if 'R1' in fname:
            sample['R1'] = fpath
            sample['R1_bid'] = bid
        else:
            sample['R2'] = fpath
            sample['R2_bid'] = bid
        samples[rg_id] = sample
    check_samples(samples)

    result = dict()
    result['read_group_sequnecing_center'] = list()
    result['read_group_sequencing_platform'] = list()
    result['read_group_platform_unit'] = list()
    result['read_group_library'] = list()
    result['tumor_type'] = list()
    result['read_group_identifier'] = list()
    result['read_group_sample_name'] = list()
    result['species'] = list()
    result['patient_id'] = list()
    result['bait_set'] = list()
    result['igo_id'] = list()
    result['run_date'] = list()
    result['R1'] = list()
    result['R2'] = list()
    result['R1_bid'] = list()
    result['R2_bid'] = list()

    for rg_id in samples:
        sample = samples[rg_id]
        for key in sample:
            result[key].append(sample[key])
    result = check_and_return_single_values(result)
    print(result)
    return result


def check_samples(samples):
    for rg_id in samples:
        r1 = samples[rg_id]['R1']
        r2 = samples[rg_id]['R2']

        expected_r2 = 'R2'.join(r1.rsplit('R1', 1))
        if expected_r2 != r2:
            print("Mismatched fastqs! Check data:")
            print("R1: %s" % r1)
            print("Expected R2: %s" % expected_r2)
            print("Actual R2: %s" % r2)


def check_and_return_single_values(data):
    single_values = ['read_group_sequnecing_center', 'read_group_library', 'read_group_sequencing_platform', 'read_group_sample_name', 'bait_set',
                     'patient_id', 'species', 'tumor_type', 'igo_id']

    for key in single_values:
        value = set(data[key])
        if len(value) == 1:
            data[key] = value.pop()
        else:
            pprint(data)
            print("Expected only one value for %s!" % key)
            print("Check import, something went wrong.")
    return data
