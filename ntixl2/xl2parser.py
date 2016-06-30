
""" The xl2parser.py module contain tools for parsing logging and report text files generated by the NTiXL2 device.

The NTiXL2 device save report and logging files in .txt format.


Todo
----

    - Create parsing function
    - return should be a :obj:`dict` data structure containing data and measurements metadata
    - consider use of `datetime` for date and time objects.
    - consider use of `pandas` for timeseries or nupyarray for simple arrays

Note
----

    - keep it as simple as possible (function where classes are not needed)

"""

from datetime import datetime


def try_parse_float(s):
    try:
        return float(s)
    except ValueError:
        return s



def parse_broadband_file(file_path):
    """

    Parameters
    ----------
    file_path
        The location of the broadband recording file to be parsed

    Returns
    -------
    dict
        A dictionary organized in sections containing metadata and a section for measurements

    """
    raw_sections = open(file_path).read().split('#')
    sections = []
    # Split up data into sections
    for sec_id, section in enumerate(raw_sections):
        if sec_id == 0: continue
        lines = []
        # Split up sections into lines to parse
        for line in section.split('\n'):
            lines.append(line.strip())
        sections.append(lines)
    sections.pop(len(sections)-1)

    dictionary = {}
    for sec_id, section in enumerate(sections):
        # Extract headline as dictionary key
        section_headline = sections[sec_id].pop(0).strip()
        dictionary[section_headline] = broadband_section_functions[sec_id](sections[sec_id])

    return dictionary


def _parse_info_section(section):
    section_dict = {}
    for line in section:
        splits = line.split('\t')
        if len(splits) != 2: continue
        section_dict[splits[0].strip().replace(':','')] = splits[1].strip()
    return section_dict


def _parse_time_section(section):
    section_dict = {}
    for line in section:
        splits = line.split('\t')
        if len(splits) != 2: continue
        section_dict[splits[0].strip().replace(':', '')] = datetime.strptime(splits[1].strip(), '%Y-%m-%d, %H:%M:%S')  # format to match: 2016-06-28, 20:05:08
    return section_dict


def _parse_broadband_data_section(section):
    line1 = section.pop(0).split('\t')
    line2 = section.pop(0).split('\t')

    headers = []

    samples = []

    for idx, part in enumerate(line1):
        headers.append(part.strip() + ('' if (idx >= len(line2) or idx <= 3) else ' ' + line2[idx].strip()))

    for line in section:
        splits = line.split('\t')
        if len(splits) < 3: continue
        sample = {}
        for idx,part in enumerate(splits):
            sample[headers[idx]] = try_parse_float(part.strip())
        samples.append(sample)

    for sample in samples:
        timestamp_string = sample['Date'] + ', ' + sample['Time']
        sample['Timestamp'] = datetime.strptime(timestamp_string, '%Y-%m-%d, %H:%M:%S') # format to match: 2016-06-28, 20:05:08
    return samples


broadband_section_functions = {
    0: _parse_info_section,
    1: _parse_info_section,
    2: _parse_time_section,
    3: _parse_broadband_data_section,
}

broadband_parse_instructions = {

}

def logging_parser(file):
    """

    Parameters
    ----------
    file

    Returns
    -------

    """
    pass

def logging_SLA_parser(file):
    """

    Parameters
    ----------
    file

    Returns
    -------

    """
    pass