#!/usr/bin/env python

""" MultiQC module to parse output from BUSCO """

from __future__ import print_function

import base64
import logging
import re
from collections import OrderedDict

from multiqc.modules.base_module import BaseMultiqcModule

# Initialise the logger
log = logging.getLogger(__name__)


class MultiqcModule(BaseMultiqcModule):
    """BUSCO module"""

    def __init__(self):

        # Initialise the parent object
        super(MultiqcModule, self).__init__(
            name="PRETEXT",
            anchor="pretext",
            href="https://github.com/wtsi-hpag/PretextView",
            info="is a tool for visualizing HiC contact maps",
            doi="",
        )
        self.pretext_data = dict()

        for f in self.find_log_files("pretext/png"):
            self.pretext_data[f["s_name"]] = base64.b64encode(f["f"].read()).decode("utf-8")

        self.pretext_data = self.ignore_samples(self.pretext_data)

        try:
            if not self.pretext_data:
                raise UserWarning

            image_format = "png"
            log.info("Found {} pretext image".format(len(self.pretext_data)))
            for image_name, image_string in self.pretext_data.items():
                img_html = '<div class="mqc-custom-content-image"><img src="data:image/{};base64,{}" /></div>'.format(
                    image_format, image_string
                )
                self.add_section(name=image_name, anchor="pretext", content=img_html)

            # nothing to write, only images (no self.write_data_file self.add_data_source)

        except UserWarning:
            pass
        except Exception as err:
            log.error(err)
            log.debug(traceback.format_exc())
