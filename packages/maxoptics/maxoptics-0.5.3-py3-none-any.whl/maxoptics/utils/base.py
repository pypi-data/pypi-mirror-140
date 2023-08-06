# coding=utf-8
from maxoptics.config import Config

from collections import defaultdict
import re
import logging

COLOR = Config.COLOR

logging.basicConfig(filename='maxoptics.log')
logger = logging.getLogger("maxoptics.sdk")


class ShadowAttr:
    def __new__(cls, _key="", *args):
        def getter(self):
            key = _key
            if not key in self.__dict__:
                self.load_data()
            res = getattr(self, key)
            if args:
                for arg in args:
                    res = res[arg]
                return res
            else:
                return res

        def setter(self, value):
            key = _key
            if isinstance(value, str) and value.isdigit():
                value = int(value)
            setattr(self, key, value)

        def deleter(self):
            key = _key
            exec(f"del self.{key}")

        return property(fget=getter)


def success_print(txt, *args, **kargs):
    if COLOR:
        print("\033[32m%s\033[0m" % txt, *args, **kargs)
    else:
        print("SUCCESS: %s\n" % txt, *args, **kargs)


def error_print(txt, *args, **kargs):
    if COLOR:
        print("\033[31m%s\033[0m" % txt, *args, **kargs)
    else:
        print("ERROR: %s\n" % txt, *args, **kargs)
    logger.error(txt)


def info_print(txt, *args, **kargs):
    if COLOR:
        print("\033[36m%s\033[0m" % txt, *args, **kargs)
    else:
        print("INFO: %s\n" % txt, *args, **kargs)
    logger.info(txt)


def warn_print(txt, *args, **kargs):
    if COLOR:
        print("\033[35m%s\033[0m" % txt, *args, **kargs)
    else:
        print("WARNING: %s\n" % txt, *args, **kargs)
    logger.warning(txt)


# Print functions


def printf(task_id, *args):
    args = map(lambda _: str(_), args)
    msg = "".join(args)
    print(f"\nTask {task_id}: " + msg + "\n")


def eprintf(task_id, *args):
    args = map(lambda _: str(_), args)
    msg = "".join(args)
    error_print(f"\nTask {task_id}: " + msg + "\n")


def sprintf(task_id, *args):
    args = map(lambda _: str(_), args)
    msg = "".join(args)
    success_print(f"\nTask {task_id}: " + msg + "\n")


def classifier(class_name, obj):
    from maxoptics.autogen import ClassColle

    patterns = {
        "ports": lambda cn, o: re.search("(Port|port|PORT)$", cn),
        "monitors": lambda cn, o: re.search("(Monitor|monitor|MONITOR)$", cn),
        "solver": lambda cn, o: re.search("^(EME|FDE|FDTD)$", cn),
        "sources": lambda cn, o: re.search("(Source|source|SOURCE)$", cn),
        "port_groups": lambda cn, o: re.search("(PortGroup|Portgroup|portgroup)$", cn),
        "polygons": lambda cn, o: str(o["type"]["base"]["name"]) == "Polygon",
    }
    for ptn in patterns:
        if isinstance(obj, ClassColle.new("GlobalMonitor")):
            return "others"
        _filter = patterns[ptn]
        is_passed = _filter(class_name, obj)
        if is_passed:
            return ptn
    return "others"


def damerau_levenshtein_distance(s1, s2):
    # Copy from jellyfish
    len1 = len(s1)
    len2 = len(s2)
    infinite = len1 + len2

    # character array
    da = defaultdict(int)

    # distance matrix
    score = [[0] * (len2 + 2) for x in range(len1 + 2)]

    score[0][0] = infinite
    for i in range(0, len1 + 1):
        score[i + 1][0] = infinite
        score[i + 1][1] = i
    for i in range(0, len2 + 1):
        score[0][i + 1] = infinite
        score[1][i + 1] = i

    for i in range(1, len1 + 1):
        db = 0
        for j in range(1, len2 + 1):
            i1 = da[s2[j - 1]]
            j1 = db
            cost = 1
            if s1[i - 1] == s2[j - 1]:
                cost = 0
                db = j

            score[i + 1][j + 1] = min(
                score[i][j] + cost,
                score[i + 1][j] + 1,
                score[i][j + 1] + 1,
                score[i1][j1] + (i - i1 - 1) + 1 + (j - j1 - 1),
            )
        da[s1[i - 1]] = i

    return score[len1 + 1][len2 + 1]


def nearest_words_with_damerau_levenshtein_distance(dic, name):
    def extract_dict(dic, name_list: list):
        for n in dic:
            if n not in name_list:
                name_list.append(n)
            if isinstance(dic[n], dict):
                extract_dict(dic[n], name_list)
        return name_list

    if isinstance(dic, dict):
        name_list = extract_dict(dic, [])
    elif isinstance(dic, list):
        name_list = dic
    else:
        raise SystemError("SDK down.")
    dis_list = []
    result_list = []
    for n in name_list:
        dis = damerau_levenshtein_distance(n, name)
        dis_list.append(dis)
        result_list.append(n)

    sorted_zipped = sorted(zip(dis_list, result_list))
    # sorted_unzipped = tuple(zip(*sorted_zipped))
    sorted_unzipped = tuple(zip(*sorted_zipped))[1][:5]
    return sorted_unzipped
