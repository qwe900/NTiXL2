
""" The xl2parser.py module contain tools for parsing logging and report text files generated by the NTiXL2 device.

The NTiXL2 device save report and logging files in .txt format.

"""

from datetime import datetime


def __try_parse_float(s):
    try:
        return float(s)
    except ValueError:
        return s


def __parse_file(file_path, function_dict):
    raw_sections = open(file_path).read().split('#')
    sections = []
    # Split up data into sections
    for sec_id, section in enumerate(raw_sections):
        if sec_id == 0: continue
        # Split up sections into lines to parse
        lines = [line.strip() for line in section.split('\n')]
        sections.append(lines)
    sections.pop(len(sections) - 1)

    dictionary = {}
    for sec_id, section in enumerate(sections):
        # Extract headline as dictionary key
        section_headline = sections[sec_id].pop(0).strip()
        dictionary[section_headline] = function_dict[sec_id](sections[sec_id])
    return dictionary


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
    broadband_section_functions = {
        0: __parse_hardware_section,
        1: __parse_measurement_setup_section,
        2: __parse_time_section,
        3: __parse_broadband_data_section,
    }
    return __parse_file(file_path, broadband_section_functions)


def parse_spectrum_file(file_path):
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
    spectrum_section_functions = {
        0: __parse_hardware_section,
        1: __parse_measurement_setup_section,
        2: __parse_time_section,
        3: __parse_spectrum_data_section,
    }
    return __parse_file(file_path, spectrum_section_functions)


def __swap_units(section, key):
    value = section[key]
    new_val = __try_parse_float(value.rsplit(' ', 1)[0])
    new_key = "{0} [{1}]".format(key, value.rsplit(' ',1)[1])
    section.pop(key, None)
    section[new_key] = new_val
    return section


def __parse_hardware_section(section):
    section_dict = __parse_info_section(section)
    mic_sensitivity_key = 'Mic Sensitivity'
    section_dict = __swap_units(section_dict, mic_sensitivity_key)
    return section_dict


def __parse_measurement_setup_section(section):
    section_dict = __parse_info_section(section)
    range_key = 'Range'
    section_dict = __swap_units(section_dict, range_key)
    section_dict[range_key + ' [dB]'] = [__try_parse_float(val) for val in section_dict[range_key + ' [dB]'].split(' - ')]
    return section_dict


def __parse_info_section(section):
    section_dict = {}
    for line in section:
        splits = line.split('\t')
        if len(splits) != 2: continue
        section_dict[splits[0].strip().replace(':','')] = __try_parse_float(splits[1].strip())
    return section_dict


def __parse_time_section(section):
    section_dict = {}
    for line in section:
        splits = line.split('\t')
        if len(splits) != 2: continue
        section_dict[splits[0].strip().replace(':', '')] = datetime.strptime(splits[1].strip(), '%Y-%m-%d, %H:%M:%S')  # format to match: 2016-06-28, 20:05:08
    return section_dict


def __parse_broadband_data_section(section):
    line1 = section.pop(0).split('\t')
    line2 = section.pop(0).split('\t')

    headers = []

    samples = []

    for idx, part in enumerate(line1):
        headers.append(part.strip() + ('' if (idx >= len(line2) or idx <= 2) else ' ' + line2[idx].strip()))

    for line in section:
        splits = line.split('\t')
        if len(splits) < 3: continue
        sample = {}
        for idx,part in enumerate(splits):
            sample[headers[idx]] = __try_parse_float(part.strip())
        samples.append(sample)

    for sample in samples:
        timestamp_string = sample['Date'] + ', ' + sample['Time']
        sample['Timestamp'] = datetime.strptime(timestamp_string, '%Y-%m-%d, %H:%M:%S') # format to match: 2016-06-28, 20:05:08
    return samples


def __parse_spectrum_data_section(section):
    section[1] = section[1].replace('[dB]', 'Hz [dB]')
    samples = __parse_broadband_data_section(section)
    for sample in samples:
        sample.pop('Band [Hz]',None)
    for sample in samples:
        freq_vs_label = {}
        for key in sample.keys():
            if '[dB]'  in key:
                freq_vs_label[__try_parse_float(key.split()[0])] = key
        sample['Spectrum_Frequencies [Hz]'] = []
        sample['Spectrum_LZeq_dt_f [dB]'] = []
        sorted_keys = list(freq_vs_label.keys())
        sorted_keys.sort()
        for key in sorted_keys:
            sample['Spectrum_Frequencies [Hz]'].append(key)
            sample['Spectrum_LZeq_dt_f [dB]'].append(sample[freq_vs_label[key]])
        for key in freq_vs_label.values():
            sample.pop(key, None)

    return samples