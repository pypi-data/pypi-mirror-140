import re

from atdf_easy.atdf import Atdf
from atdf_easy.atdf_variables import AtdfRecords, FIRST_SEPARATOR, SEP


def read_atdf_file(file_path: str, skip_corrupted_records: bool = False) -> Atdf:
    with open(file_path, 'r') as f:
        rows: AtdfRecords = {}
        for line in f.readlines():
            if line.strip() == '':  # ignore blank lines
                continue
            if not (re.findall(r"^[a-zA-Z]+:", line)):  # check for corrupted records
                if not skip_corrupted_records:
                    raise ValueError(f'this record is corrupted : {line}')
                else:
                    print(f'WARNING : skipped corrupted record : {line}')
                    continue
            split_line = line.split(FIRST_SEPARATOR, 1)
            record_name = split_line[0]
            if len(split_line) == 1:
                values = ''
            else:
                values = line.split(FIRST_SEPARATOR, 1)[1]

            values = values.replace('\n', '')
            values_as_list = values.split(SEP)
            record = rows.get(record_name, [])
            rows[record_name] = record
            record.append(values_as_list)
    return Atdf(values=rows)
