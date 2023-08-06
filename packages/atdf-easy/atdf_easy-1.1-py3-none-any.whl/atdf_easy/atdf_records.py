from typing import List


class AtdfRecords:
    def __init__(self, values: List[List[str]]):
        self._sanity_check(values=values)
        self._values = values

    @staticmethod
    def _sanity_check(values):
        errors = []
        for values_ in values:
            if not isinstance(values_, list):
                errors.append(f'{values_} incorrect: expected a list')
            if len(values_) == 0:
                errors.append('None incorrect: expected a non empty list')
            for value in values_:
                if not isinstance(value, str):
                    errors.append(f'{value} incorrect: expected a string')
        if errors:
            raise ValueError('\n'.join(errors))

    def __getitem__(self, item):
        if not isinstance(item, tuple) and len(item) == 2:
            raise IndexError
        if isinstance(item[0], slice):
            return [k[item[1]] for k in self._values[item[0]]]
        return self._values[item[0]][item[1]]

    def __setitem__(self, key, value):
        if not isinstance(key, tuple) and len(key) == 2:
            raise IndexError
        if isinstance(key[0], slice) and isinstance(key[1], slice):
            if isinstance(value, str):
                for val in self._values[key[0]]:
                    start = key[1].start if key[1].start else 0
                    stop = key[1].stop if key[1].stop else len(val)
                    for index in range(start, stop):
                        val[index] = value
            elif isinstance(value, list):
                val: List[str]
                if not len(value) == len(self._values[key[0]]):
                    raise ValueError('wrong size value passed')
                for val, new_val in zip(self._values[key[0]], value):
                    start = key[1].start if key[1].start else 0
                    stop = key[1].stop if key[1].stop else len(val)
                    for index in range(start, stop):
                        val[index] = new_val
            else:
                raise ValueError('expected a string or a list')
        elif isinstance(key[0], int) and isinstance(key[1], int):
            self._values[key[0]][key[1]] = value
        elif isinstance(key[0], slice) and isinstance(key[1], int):
            if isinstance(value, str):
                for val in self._values[key[0]]:
                    val[key[1]] = value
            elif isinstance(value, list):
                val: List[str]
                if not len(value) == len(self._values[key[0]]):
                    raise ValueError('wrong size value passed')
                for val, new_val in zip(self._values[key[0]], value):
                    val[key[1]] = new_val
        else:
            raise NotImplementedError
        self._sanity_check(values=self._values)

    def __repr__(self):
        return "\n".join(map(lambda x: str(x), list(map(lambda x: "|".join(x), self._values))))

    def __eq__(self, other):
        if isinstance(other, list):
            other = AtdfRecords(other)
        return self._values == other._values
