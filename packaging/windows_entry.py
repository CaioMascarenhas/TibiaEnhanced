"""Entrada absoluta para o executável; diagnóstico opcional usa perfil temporário."""

import argparse
import os
import sys

if "--synthetic-source" in sys.argv:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic-source", required=True)
    parser.add_argument("--source-control", required=True)
    parser.add_argument("--source-status", required=True)
    args = parser.parse_args()
    from tibiaenhanced.services.bundle_validation import run_source

    raise SystemExit(run_source(args.synthetic_source, args.source_control, args.source_status))

if "--smoke-test-report" in sys.argv:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test-report", required=True)
    parser.add_argument("--smoke-test-screenshot")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()
    if args.headless:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from tibiaenhanced.services.bundle_validation import run_validation

    raise SystemExit(run_validation(args.smoke_test_report, args.smoke_test_screenshot,
                                    native=not args.headless))

from tibiaenhanced.app import main

raise SystemExit(main())
