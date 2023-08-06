from pathlib import Path
from typing import List

from atdf_easy.atdf_records import AtdfRecords
from atdf_easy.atdf_variables import SEP


class Atdf:
    def __init__(self, values: dict[str, List[List[str]]]):
        self._sanity_check(values)
        self.atdf_records = {record_name: AtdfRecords(atdf_records) for record_name, atdf_records in values.items()}

    @staticmethod
    def _sanity_check(records: dict[str, List[List[str]]]):
        errors = []
        for record, atdf_records in records.items():
            if not atdf_records:
                errors.append(f'{atdf_records} incorrect for record {record} expected a list of list')
        if errors:
            raise ValueError('\n'.join(errors))

    def __repr__(self):
        return '\n'.join([f'==={record}===\n{values}' for record, values in self.atdf_records.items()])

    def __eq__(self, other):
        return self.atdf_records == other.atdf_records

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.atdf_records[item]
        else:
            return self.atdf_records[item[0]][item[1], item[2]]

    def __setitem__(self, key, value):
        self.atdf_records[key[0]][key[1], key[2]] = value

    def to_file(self, path: str, overwrite=False) -> None:
        if Path(path).exists() and not overwrite:
            raise FileExistsError
        with open(path, 'w') as f:
            for record_name, atdf_records in self.atdf_records.items():
                for atdf_record in atdf_records._values:  # TODO : implement iterator on AtdfRecords
                    parsed_values = f'{SEP}'.join(atdf_record)
                    line = f"{record_name}:{parsed_values}\n"
                    f.write(line)

    def update_column_value(self, record_name, index, new_value: str, allow_append: bool = False) -> None:
        records_to_update: AtdfRecords = self.atdf_records[record_name]
        for values in records_to_update._values:
            try:
                values[index] = new_value
            except IndexError:
                if allow_append:
                    empty_value_to_add = index - len(values)
                    for k in range(empty_value_to_add):
                        values.append('')
                    values.append(new_value)
                else:
                    raise IndexError

    def append_record(self, record_name, new_value: List[str]):
        records_to_update: AtdfRecords = self.atdf_records[record_name]
        records_to_update._values.append(new_value)
