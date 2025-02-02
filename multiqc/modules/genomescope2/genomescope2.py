#!/usr/bin/env python

""" MultiQC module to parse output from genomescope """

from __future__ import print_function

import base64
import logging
import re
from collections import OrderedDict

from multiqc.modules.base_module import BaseMultiqcModule
from multiqc.plots import table

# Initialise the logger
log = logging.getLogger(__name__)


class MultiqcModule(BaseMultiqcModule):
    """Genomescope2 module"""

    def __init__(self):

        # Initialise the parent object
        super(MultiqcModule, self).__init__(
            name="Genomescope2",
            anchor="Genomescope2",
            href="https://github.com/tbenavi1/genomescope2.0",
            info="Reference-free profiling of polyploid genomes.",
            doi="10.1038/s41467-020-14998-3",
        )

        # Find and load any GENOMESCOPE reports
        self.summary_data = dict()

        for f in self.find_log_files("genomescope2/summary"):
            self.parse_summary_log(f)

        self.find_figures()

        self.summary_data = self.ignore_samples(self.summary_data)

        if not len(self.summary_data) and not len(self.genomescope_png):
            raise UserWarning
        if len(self.summary_data):
            log.info(f"Found {len(self.summary_data)} log reports")
        if len(self.genomescope_png):
            log.info(f"Found {len(self.genomescope_png)} images")

        # Write parsed report data to a file
        self.write_data_file(self.summary_data, "multiqc_genomescope_summary")

        self.add_section(name="Summary", anchor="genomescope-summary", plot=self.summary_table())

        self.plot_figures()

    def parse_summary_log(self, f):
        self.add_data_source(f)
        s_name = f["s_name"]
        block = -1
        i = 0
        content = []
        for l in f["f"].splitlines():
            if l.startswith("property"):
                block = i
            if block != -1:
                content.append(l)
            i = i + 1
        self.summary_data[s_name] = dict()
        self.legends = []
        for l in content[1:]:
            items = re.split(r"\s{2,}", l.strip())
            this_name = items[0]
            this_val = items[2].rstrip("%bp")
            try:
                this_val = float(this_val)
            except ValueError:
                pass
            self.summary_data[s_name][this_name] = this_val
            self.legends.append(this_name)

    def summary_table(self):
        """Take the parsed stats from the Genomescope report and add some to the
        General Statistics table at the top of the report"""
        headers = OrderedDict()
        for legend in self.legends:
            headers[legend] = {
                "title": legend,
                "description": legend,
                "scale": "RdYlGn",
            }

        config = {
            "id": "summary_table",
            "namespace": "GENOMESCOPE",
            "min": 0,
        }
        return table.plot(self.summary_data, headers, config)

    def find_figures(self):
        self.genomescope_png = dict()
        for f in self.find_log_files("genomescope2/png"):
            self.genomescope_png[f["s_name"]] = base64.b64encode(f["f"].read()).decode("utf-8")

        self.genomescope_png = self.ignore_samples(self.genomescope_png)

    def plot_figures(self):
        for image_name, image_string in self.genomescope_png.items():
            img_html = f'<div class="mqc-custom-content-image"><img src="data:image/png;base64,{image_string}" /></div>'
            self.add_section(name=image_name, anchor="Genomescope2", content=img_html)
