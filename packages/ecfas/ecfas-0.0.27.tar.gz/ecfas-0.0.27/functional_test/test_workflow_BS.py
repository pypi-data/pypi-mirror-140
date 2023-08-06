import argparse
import os
import shutil

import pytest

import ecfas.cmems_operational_fullworkflow as wf
import ecfas.quality_checks as qc


def setup_module():
    global test_dir
    test_dir = os.path.dirname(os.path.abspath(__file__))
    global outputs
    outputs = os.path.join(os.getcwd(), 'test_outputs')
    if not os.path.exists(outputs):
       os.mkdir(outputs)
    global region
    region = 'BS'
    global date
    date = '20220125_000000'
    region_dir = os.path.join(os.getcwd(), 'test_outputs', region)
    if os.path.exists(region_dir):
        shutil.rmtree(region_dir)


@pytest.mark.incremental
def test_workflow():
    """ The config we have been manually testing with """
    cli_args = argparse.Namespace()
    cli_args.region = region
    cli_args.reanal = False
    cli_args.t0 = date
    cli_args.debug = True
    cli_args.config = os.path.join(test_dir, 'ecfas.cnf')
    wf.execute_workflow(cli_args)


@pytest.mark.incremental
def test_quality_check():
        baselines = os.path.join(os.getcwd(), 'baselines')
        ok = qc.run_checks(outputs, baselines, region, date)
        assert ok
