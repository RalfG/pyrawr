"""Python wrapper around the ThermoRawFileParser command line interface."""

import json
import os
import subprocess
import tempfile

import semver


class ThermoRawFileParser:
    """Wrapper around ThermoRawFileParser CLI."""
    def __init__(
        self, executable="thermorawfileparser", docker_image=None,
    ):
        """
        Wrapper around ThermoRawFileParser CLI.

        Parameters
        ----------
        executable: str
            ThermoRawFileParser shell command. For example,
            ``thermorawfileparser`` or ``mono ThermoRawFileParser.exe``.
        docker_image: str, optional
            Docker image with ThermoRawFileParser. Requires
            the ``docker run`` CLI command.

        Attributes
        ----------
        version_requirement: str
            ThermoRawFile semver version requirement.
        installed_version: str
            Installed ThermoRawFileParser version.

        Examples
        --------
        >>> from pyrawr import ThermoRawFileParser
        >>> trfp = ThermoRawFileParser(
        ...     executable="thermorawfileparser",
        ...     docker_image="quay.io/biocontainers/thermorawfileparser:1.3.3--ha8f3691_1"
        ... )
        >>> trfp.parse("OR4_110719_OB_PAR14_sSCX_fr10.raw")

        >>> trfp.metadata("OR4_110719_OB_PAR14_sSCX_fr10.raw")
        {'FileProperties': [{'accession': 'NCIT:C47922', 'cvLabel': 'NCIT' ... }]}

        >>> trfp.query("OR4_110719_OB_PAR14_sSCX_fr10.raw", "508,680")
        [{'mzs': [204.8467254638672,
        262.4529113769531,
        309.53961181640625,
        ...

        >>> trfp.xic(
        ...     "OR4_110719_OB_PAR14_sSCX_fr10.raw",
        ...     [{"mz":488.5384, "tolerance":10, "tolerance_unit":"ppm"}],
        ... )
        {'OutputMeta': {'base64': False, 'timeunit': 'minutes'},
        'Content': [{'Meta': {'MzStart': 488.53351461600005,
            'MzEnd': 488.543285384,
            'RtStart': 0.007536666666666666,
            'RtEnd': 179.99577166666666},
        'RetentionTimes': [0.007536666666666666,
            0.022771666666666666,
            0.036936666666666666,
            ...

        """
        # Arguments
        self.executable = executable
        self.docker_image = docker_image

        # Properties
        self.version_requirement = ">=1.3.3"
        self.installed_version = None

        # Validate installation
        self._validate_install()

    def parse(self, input_file, output_format=None, options=None):
        """
        Parse raw file to one of the supported output formats.

        Parameters
        ----------
        input_file: str
            Path to input file.
        output_format: str, optional
            Output format. One of ``mgf``, ``mzml``, ``indexed_mzml``, ``parquet``, or
            ``scan_info``.
        options: List
            List of other CLI options to pass to ThermoRawFileParser. See
            `ThermoRawFileParser docs <https://github.com/compomics/ThermoRawFileParser#usage>`__
            for more info.

        """
        formats = {
            "mgf": "0",
            "mzml": "1",
            "indexed_mzml": "2",
            "parquet": "3",
            "scan_info": "4",
        }
        input_file = os.path.abspath(input_file)
        cmd_options = ["-i", input_file]
        if output_format:
            cmd_options.extend(["-f", formats[output_format.lower()]])
        if options:
            cmd_options.extend(options)

        _ = self._run_command(cmd_options, files=[input_file])

    def metadata(self, input_file):
        """
        Get raw file metadata as Python dictionary.

        Parameters
        ----------
        input_file: str
            Path to input file.

        Returns
        -------
        metadata: dict
            Dictionary containing raw file metadata.

        """
        input_file = os.path.abspath(input_file)
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = os.path.join(tmp_dir, "meta.json")
            cmd_options = ["-i", input_file, "-c", output_file, "-m", "0"]
            _ = self._run_command(cmd_options, files=[input_file, output_file])
            with open(output_file) as f:
                metadata = json.load(f)
        return metadata

    def query(self, input_file, scans, options=None):
        """
        Retrieve specific spectra by scan number in ProXI format.

        Parameters
        ----------
        input_file: str
            Path to input file.
        scans: str
            Scan numbers, e.g. ``1-5, 20, 25-30``.
        options: list
            List of other CLI options to pass to ThermoRawFileParser. See
            `ThermoRawFileParser docs <https://github.com/compomics/ThermoRawFileParser#query-subcommand>`__
            for more info.

        Returns
        -------
        spectra: list
            List of spectra in ProXI format.

        """
        input_file = os.path.abspath(input_file)
        cmd_options = ["query", "-i", input_file, "-n", scans, "-s"]
        if options:
            cmd_options.extend(options)
        cmd_out = self._run_command(cmd_options, files=[input_file])
        return json.loads(cmd_out.stdout.decode().strip())

    def xic(self, input_file, query, base64=False):
        """
        Retrieve one or more chromatograms based on a query.

        Parameters
        ----------
        input_file: str
            Path to input file.
        query: list
            List of query dictionaries. See
            `ThermoRawFileParser docs <https://github.com/compomics/ThermoRawFileParser#xic-subcommand>`__
            for more info.
        base64: boolean, optional
            Encode the content of the xic vectors as base 64.

        Returns
        -------
        xic: dict
            Dictionary containing XICs.

        """
        input_file = os.path.abspath(input_file)
        with tempfile.TemporaryDirectory() as tmp_dir:
            query_file = os.path.join(tmp_dir, 'query.json')
            with open(query_file, 'wt') as f:
                json.dump(query, f)
            cmd_options = ["xic", "-i", input_file, "-j", query_file, "-s"]
            if base64:
                cmd_options.append('--base64')
            cmd_out = self._run_command(cmd_options, files=[input_file, query_file])
        return json.loads(cmd_out.stdout.decode().strip())

    def _validate_install(self):
        cmd_out = self._run_command(["--version"])
        if cmd_out.returncode != 0:
            raise ThermoRawFileParserInstallationError(cmd_out.stderr.decode().strip())
        self.installed_version = cmd_out.stdout.decode().strip()
        if not semver.match(self.installed_version, self.version_requirement):
            raise ThermoRawFileParserInstallationError(
                f"Installed version {self.installed_version} does not match "
                f"requirement {self.version_requirement}"
            )

    def _run_command(self, options, files=None, check=True):
        options = [str(o) for o in options]
        if self.docker_image:
            docker_args = []
            if files:
                file_paths = set([os.path.abspath(f) for f in files])
                file_paths = set([os.path.dirname(f) for f in file_paths])
                for f in file_paths:
                    docker_args.extend(["-v", f"{f}:{f}"])
            cmd = (
                ["docker", "run"]
                + docker_args
                + [self.docker_image]
                + self.executable.split(" ")
                + options
            )
        else:
            cmd = [self.executable] + options

        try:
            cmd_out = subprocess.run(cmd, check=False, capture_output=True)
        except FileNotFoundError as e:
            raise ThermoRawFileParserInstallationError(e)
        if check and not cmd_out.returncode == 0:
            raise ThermoRawFileParserRunError(
                f"Error running command {cmd}:\n{cmd_out.stderr.decode()}"
            )

        return cmd_out


class ThermoRawFileParserError(Exception):
    """General ThermoRawFileParser error."""
    pass


class ThermoRawFileParserInstallationError(ThermoRawFileParserError):
    """Could not find ThermoRawFileParser CLI."""
    pass


class ThermoRawFileParserRunError(ThermoRawFileParserError):
    """Error running ThermoRawFileParser."""
    pass
