import numpy as np

from typing import Tuple, Dict, Set, Callable, Any

RawDoc = Dict[str, Any]


class FilterCondition:
    def __init__(self) -> None:
        self.field = None

    def __call__(self, doc: RawDoc) -> bool:
        raise NotImplementedError()

    def __hash__(self) -> int:
        raise NotImplementedError()

    def __eq__(self, o: object) -> bool:
        raise NotImplementedError()


# TODO hashcode + equals
class CalcFieldFor(FilterCondition):
    def __init__(self, cond: FilterCondition, mapop: Callable[[RawDoc], Any]):
        self.cond = cond
        self.mapop = mapop
        self.new_field_name = cond.field

    def __call__(self, doc: RawDoc) -> bool:
        v = self.mapop(doc)
        doc[self.new_field_name] = v
        return self.cond(doc)

    def __hash__(self) -> int:
        return hash(self.cond)

    def __eq__(self, o: object) -> bool:
        return (self.cond == o)

    def __repr__(self) -> str:
        return repr(self.cond)


class Eq(FilterCondition):
    def __init__(self, field: str, ethalon_val: Any) -> None:
        self.field = field
        if isinstance(ethalon_val, list):
            self.ethalon_val = tuple(ethalon_val)
        else:
            self.ethalon_val = ethalon_val

    def __call__(self, doc: RawDoc) -> bool:
        val = doc.get(self.field)
        if isinstance(val, list):
            val = tuple(val)
        return val == self.ethalon_val

    def __hash__(self) -> int:
        return hash((self.field, self.ethalon_val))

    def __eq__(self, o: object) -> bool:
        cls = Eq
        if isinstance(o, CalcFieldFor):
            o = o.cond
        if isinstance(o, cls):
            return (self.field == o.field) and (self.ethalon_val == o.ethalon_val)
        return False

    def __repr__(self) -> str:
        return f"{self.field} == {self.ethalon_val}"


class OneOf(FilterCondition):
    def __init__(self, field: str, one_of_vals: Set[Any]):
        if isinstance(one_of_vals, list) or isinstance(one_of_vals, tuple):
            if len(one_of_vals) > 0 and isinstance(one_of_vals[0], list):
                self.one_of_vals = set([tuple(t) for t in one_of_vals])
            else:
                self.one_of_vals = set(one_of_vals)
        elif isinstance(one_of_vals, set):
            self.one_of_vals = one_of_vals
        else:
            raise Exception('vals is not Set')
        self.field = field

    def __call__(self, doc: RawDoc) -> bool:
        val = doc.get(self.field)
        if isinstance(val, list):
            val = tuple(val)
        return val in self.one_of_vals

    def __hash__(self) -> int:
        return hash((self.field, tuple(self.one_of_vals)))

    def __eq__(self, o: object) -> bool:
        cls = OneOf
        if isinstance(o, CalcFieldFor):
            o = o.cond
        if isinstance(o, cls):
            return (self.field == o.field) and (self.one_of_vals == o.one_of_vals)
        return False

    def __repr__(self) -> str:
        return f"{self.field} one_of {self.one_of_vals}"


Range = Tuple[Any, Any]


class InRange(FilterCondition):
    def __init__(self, field: str, range: Range):
        self.field = field
        if isinstance(range, list):
            self.range = tuple(range)
        else:
            self.range = range

        if len(self.range) != 2:
            raise Exception('bad range definition, should be list [min, max]')

    def __call__(self, doc: RawDoc) -> bool:
        val = doc.get(self.field)
        if val == None:
            return False
        minb = val >= self.range[0] if self.range[0] else True
        maxb = val <= self.range[1] if self.range[1] else True

        return minb and maxb

    def __hash__(self) -> int:
        return hash((self.field, self.range))

    def __eq__(self, o: object) -> bool:
        cls = InRange
        if isinstance(o, CalcFieldFor):
            o = o.cond
        if isinstance(o, cls):
            return (self.field == o.field) and (self.range == o.range)
        return False

    def __repr__(self) -> str:
        return f"{self.field} in [{self.range[0]},{self.range[1]}]"


class Include(FilterCondition):
    def __init__(self, field: str, vals: Set[Any]):
        self.field = field
        if isinstance(vals, list) or isinstance(vals, tuple):
            self.vals = set(vals)
        elif isinstance(vals, set):
            self.vals = vals
        else:
            raise Exception(f'vals is not Set, vals is {type(vals)}')

    def __call__(self, doc: RawDoc) -> bool:
        dvals = set(doc.get(self.field, []))
        return dvals.intersection(self.vals) == self.vals

    def __hash__(self) -> int:
        return hash((self.field, tuple(self.vals)))

    def __eq__(self, o: object) -> bool:
        cls = Include
        if isinstance(o, CalcFieldFor):
            o = o.cond
        if isinstance(o, cls):
            return (self.field == o.field) and (self.vals == o.vals)
        return False

    def __repr__(self) -> str:
        return f"{self.field} include {self.vals}"


class MoreThen(FilterCondition):
    def __init__(self, field: str, min_val: Any):
        self.field = field
        self.min_val = min_val

    def __call__(self, doc: RawDoc) -> bool:
        val = doc.get(self.field)
        return (val > self.min_val)

    def __hash__(self) -> int:
        return hash((self.field, self.min_val))

    def __eq__(self, o: object) -> bool:
        cls = MoreThen
        if isinstance(o, CalcFieldFor):
            o = o.cond
        if isinstance(o, cls):
            return (self.field == o.field) and (self.min_val == o.min_val)
        return False

    def __repr__(self) -> str:
        return f"{self.field} > {self.min_val}"


class LessThen(FilterCondition):
    def __init__(self, field: str, max_val: Any):
        self.field = field
        self.max_val = max_val

    def __call__(self, doc: RawDoc) -> bool:
        val = doc.get(self.field)
        return (val < self.max_val)

    def __hash__(self) -> int:
        return hash((self.field, self.max_val))

    def __eq__(self, o: object) -> bool:
        cls = LessThen
        if isinstance(o, CalcFieldFor):
            o = o.cond
        if isinstance(o, cls):
            return (self.field == o.field) and (self.max_val == o.max_val)
        return False

    def __repr__(self) -> str:
        return f"{self.field} < {self.max_val}"


class DistLessThan(FilterCondition):
    def __init__(self, field: str, anchor: Tuple[float], max_dist: float):
        self.field = field
        self.max_dist = max_dist
        self.anchor = anchor

    def __call__(self, doc: RawDoc) -> bool:
        val = doc.get(self.field)
        if len(val) == 2:
            return np.linalg.norm(np.array(val) - np.array(self.anchor)) < self.max_dist
        else:
            return False

    def __hash__(self) -> int:
        return hash((self.field, self.anchor, self.max_dist))

    def __eq__(self, o: object) -> bool:
        cls = DistLessThan
        if isinstance(o, CalcFieldFor):
            o = o.cond
        if isinstance(o, cls):
            return (self.field == o.field) and (self.anchor == o.anchor) and (self.max_dist == o.max_dist)
        return False

    def __repr__(self) -> str:
        return f"Euclidian({self.field}, {self.anchor}) < {self.max_dist}"


class AlwaysFail(FilterCondition):
    def __init__(self, field: str):
        self.field = field

    def __call__(self, doc: RawDoc) -> bool:
        return False

    def __hash__(self) -> int:
        return hash(self.field)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, AlwaysFail):
            return (self.field == o.field)
        return False

    def __repr__(self) -> str:
        return f"FAIL"


class And(FilterCondition):
    def __init__(self, *conds: Set[FilterCondition]):
        if isinstance(conds, list) or isinstance(conds, tuple):
            self.conds = set(conds)
        elif isinstance(conds, set):
            self.conds = conds
        else:
            raise Exception('conds is not a set')

    def __call__(self, doc: RawDoc) -> bool:
        return all(c(doc) for c in self.conds)

    def __hash__(self) -> int:
        return hash(tuple(self.conds))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, And):
            return (self.conds == o.conds)
        return False

    def __repr__(self) -> str:
        return f"And({self.conds})"


class CheckIsBW(FilterCondition):
    def __call__(self, doc: RawDoc) -> bool:
        r, g, b = doc['dominant_color']['red'], doc['dominant_color']['green'], \
                  doc['dominant_color']['blue']
        return b == r and b == g

    def __hash__(self) -> int:
        return hash('check_is_bw')

    def __eq__(self, o: object) -> bool:
        cls = CheckIsBW
        if isinstance(o, CalcFieldFor):
            o = o.cond
        if isinstance(o, cls):
            return True
        return False

    def __repr__(self) -> str:
        return "IsBW?"


class Or(FilterCondition):
    def __init__(self, *conds: Set[FilterCondition]):
        if isinstance(conds, list) or isinstance(conds, tuple):
            self.conds = set(conds)
        elif isinstance(conds, set):
            self.conds = conds
        else:
            raise Exception('conds is not a set')

    def __call__(self, doc: RawDoc) -> bool:
        for c in self.conds:
            if c(doc):
                return True
        return False

    def __hash__(self) -> int:
        return hash(tuple(self.conds))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Or):
            return (self.conds == o.conds)
        return False

    def __repr__(self) -> str:
        return f"Or({self.conds})"


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def dict2filter(filters: Dict[str, Any]) -> FilterCondition:
    filters_acc = []

    def calc_faces(doc):
        return len(doc['faces_objects'])

    def calc_genders(doc):
        return set([f['gender'] for f in doc['faces_objects']])

    def calc_min_adges(doc):
        adges = [f['age'].replace('(', '').replace(')', '').split('-') \
                 for f in doc['faces_objects']]
        if len(adges) > 0:
            mina, maxa = zip(*[(int(a[0]), int(a[1])) for a in adges])
            return min(mina)
        else:
            return 0

    def calc_max_adges(doc):
        adges = [f['age'].replace('(', '').replace(')', '').split('-') \
                 for f in doc['faces_objects']]
        if len(adges) > 0:
            mina, maxa = zip(*[(int(a[0]), int(a[1])) for a in adges])
            return max(maxa)
        else:
            return 100

    def color(doc):
        return (
            doc['dominant_color']['red'],
            doc['dominant_color']['green'],
            doc['dominant_color']['blue']
        )

    for key, value in filters.items():

        if key in ['id', 'url', 'has_collections', 'has_model_release',
                   'created_at', 'city', 'country']:
            if value == None:
                filters_acc.append(AlwaysFail(key))
            elif not (isinstance(value, list) or isinstance(value, tuple)):
                filters_acc.append(Eq(key, value))
            elif len(value) == 0:
                filters_acc.append(AlwaysFail(key))
            elif (len(value) > 0) and isinstance(value[0], list):
                filters_acc.append(Or(*(Eq(key, tuple(v)) for v in value)))
            else:
                filters_acc.append(Eq(key, tuple(value)))
        elif key in ['source_id']:
            if value != None:
                filters_acc.append(OneOf(key, value))
            else:
                filters_acc.append(AlwaysFail(key))
        elif key == 'source_ids':
            if isinstance(value, list):
                filters_acc.append(OneOf('source_id', value))
            else:
                print('bad source_ids ', value)
                filters_acc.append(AlwaysFail('source_id'))
        elif key in ['image_resolution']:
            if value == None:
                filters_acc.append(AlwaysFail(key))
            elif isinstance(value, int):
                filters_acc.append(Eq(key, value))
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], list):
                filters_acc.append(OneOf(key, value))
            elif isinstance(value, list):
                filters_acc.append(InRange(key, value))
            else:
                print('bad image_resolution ', value)
        elif key in ['aspect_ratio']:
            if value == None:
                filters_acc.append(AlwaysFail(key))
            else:
                if isinstance(value, list) or isinstance(value, tuple):
                    if (len(value) > 0) and (not isinstance(value[0], list)):
                        filters_acc.append(InRange(key, value))
                    else:
                        filters_acc.append(Or(*(InRange(key, v) for v in value)))
                else:
                    filters_acc.append(Eq(key, value))

        elif key == 'base_color':
            if value == None:
                filters_acc.append(AlwaysFail(key))

            if value == 'bw':
                filters_acc.append(CheckIsBW())
            else:
                r, g, b = hex_to_rgb(value)

                filters_acc.append(
                    CalcFieldFor(DistLessThan('base_color', (r, g, b), 100), color)
                )

        elif (key == 'coordinates'):
            if (isinstance(value, list) or isinstance(value, tuple)) and (len(value) == 2):
                x, y = value[0], value[1]
                distance = filters.get('distance', 10)

                filters_acc.append(
                    DistLessThan('coordinates', (x, y), distance)
                )
            else:
                filters_acc.append(AlwaysFail(key))

        elif (key == 'tags') and (value != None):
            filters_acc.append(Include(key, value))

        elif (key == 'people'):
            if value == None:
                filters_acc.append(AlwaysFail(key))
            faces_acc = []
            for v in value:
                if v == 'one':
                    faces_acc.append(CalcFieldFor(Eq('people', 1), calc_faces))
                elif v == 'two':
                    faces_acc.append(CalcFieldFor(Eq('people', 2), calc_faces))
                elif v == 'many':
                    faces_acc.append(CalcFieldFor(MoreThen('people', 2), calc_faces))
            filters_acc.append(Or(*faces_acc))

        elif (key == 'genders'):
            if value == None:
                filters_acc.append(AlwaysFail(key))
            faces_acc = []
            if value == 'f':
                filters_acc.append(CalcFieldFor(Include('genders',
                                                        set(['Female'])), calc_genders))
            elif value == 'm':
                filters_acc.append(CalcFieldFor(Include('genders',
                                                        set(['Male'])), calc_genders))

        elif (key == 'face_ages'):
            if value == None:
                filters_acc.append(AlwaysFail(key))
            adgesf = []
            if value[0] != None:
                adgesf.append(CalcFieldFor(LessThen('face_ages_max', value[1]), calc_max_adges))
            if value[1] != None:
                adgesf.append(CalcFieldFor(MoreThen('face_ages_min', value[0]), calc_min_adges))
            filters_acc.append(And(*adgesf))

    return And(*tuple(filters_acc))
