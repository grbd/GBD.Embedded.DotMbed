﻿"""
Represents the Depend settings
"""

# Always try to import cElementTree since it's faster if it exists
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from os.path import join, abspath, exists
from scripts.script_logs import ScriptLogs
from scripts.dep_src_base import DepSource

# XML Settings for Download of Depends
class DependSettings(object):

    def __init__(self):
        """Dependency Settings"""
        super().__init__()
        self.log = ScriptLogs.getlogger()

        # XML Root Tag
        self.xmlroot = None

        # Directory properties
        self.DepsDirectory = ""
        self.ArchiveDirectory = ""
        self.GCCVersion = ""

        # List of Sources
        self.sources = []

    def read_element(self, tag):
        """Read XML Value Element"""
        nextval = next(self.xmlroot.iter(tag), None)
        if nextval == None : raise ValueError('Element not found: ' + tag)
        return nextval.text

    def loadxml(self, filepath):
        """Load XML"""
        # Load in the xml
        tree = ET.ElementTree(file=filepath)
        self.xmlroot = tree.getroot()
        if self.xmlroot.tag != 'DependSettings':
            raise ValueError('Root Element is not DependSettings')

        # Directory Settings
        self.DepsDirectory = self.read_element('DepsDirectory')
        self.DepsDirectory = abspath(self.DepsDirectory)
        self.ArchiveDirectory = self.read_element('ArchiveDirectory')
        self.ArchiveDirectory = join(self.DepsDirectory, self.ArchiveDirectory)
        self.GCCVersion = self.read_element('GCCVersion')

        # Set the Archive directory for downloaded sources
        DepSource.ArchiveDir = self.ArchiveDirectory
        # Set the root Extract directory for extracting sources
        DepSource.RootExtractDir = self.DepsDirectory

        # Load in the list of download sources
        self.sources = DepSource.parsexml(self.xmlroot)
        return

    def getdeps(self):
        """Download and Extract Sources"""
        for source in self.sources:
            self.log.info("")
            self.log.info("#####################################################")

            # Skip anything already extracted
            extractdir = abspath(join(DepSource.RootExtractDir, source.destsubdir))
            if exists(extractdir):
                self.log.warn("Deps Subdir: " + source.destsubdir + " already exists, skipping")
                continue

            extracted = False
            downloaded = source.download()
            if downloaded == False:
                self.log.error("Download Failed")
            else:
                extracted = source.extract()

            # Remove the archive file
            if source.destsubdir != "atmel-asf":
                source.remove_archivefile()

        # Check for ASF Sources
        if not exists(join(self.DepsDirectory, "atmel-asf")):
            self.log.warn("There was no Atmel ASF Archive file found")
            self.log.warn("asf is not required but you can manually download the below file for the Atmel Source")
            self.log.warn("http://www.atmel.com/tools/avrsoftwareframework.aspx?tab=overview")
            self.log.warn("So far this is only used for porting mbed to sam based mcu's")
        return