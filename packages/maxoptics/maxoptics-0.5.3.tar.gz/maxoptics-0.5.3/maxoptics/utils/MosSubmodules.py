import re
from maxoptics.base.BaseContainer import BaseSearchContainer

from maxoptics.utils.base import damerau_levenshtein_distance


class PublicMaterials(BaseSearchContainer):
    # from maxoptics.sdk import MaxOptics
    def __init__(self, mos):
        self.mos = mos
        self._cached = []

    def all(self):
        if self._cached:
            return self._cached
        else:
            self._cached = self.mos.post(url="get_public_materials", token=self.mos.token)["result"]["public_materials"]
            return self._cached

    def reload(self):
        self._cached = self.mos.post(url="get_public_materials", token=self.mos.token)["result"]["public_materials"]

    def _get_index(self, keyval: str):
        names = list(map(lambda _: _["name"], list(self.all())))
        # heads = list(map(lambda _: str(re.findall("^[^\\-\\(]+", _)[0]).strip(), names))
        # if keyval in heads:
        #     return heads.index(keyval)
        # else:
        for i, v in enumerate(names):
            if keyval == v:
                return i

        # Not Found
        print(f"The material {keyval} is not found, please select one of these:")
        for name in names:
            print("\t", name)
        raise KeyError

    def __getitem__(self, keyval: str):
        return self.all()[self._get_index(keyval=keyval)]

    def __setitem__(self, keyval: str, val):
        raise NotImplementedError("Changing public material is NOT allowed")


class UserMaterials(BaseSearchContainer):
    # from maxoptics.sdk import MaxOptics
    def __init__(self, mos, project_type):
        self.mos = mos
        self._cached = []
        self.project_type = project_type

    def all(self):
        if self._cached:
            return self._cached
        else:
            self._cached = self.mos.post(url="search_materials", token=self.mos.token, project_type=self.project_type)[
                "result"
            ]["result"]
            return self._cached

    def reload(self):
        self._cached = self.mos.post(url="search_materials", token=self.mos.token, project_type=self.project_type)[
            "result"
        ]["result"]

    def _get_index(self, keyval: str):
        names = list(map(lambda _: _["name"], list(self.all())))
        # heads = list(map(lambda _: str(re.findall("^[^\\-\\(_]+", _)[0]).strip(), names))
        # if keyval in heads:
        #     return heads.index(keyval)
        # else:
        for i, v in enumerate(names):
            if keyval == v:
                return i
        # Not Found
        print(f"Material {keyval} is not found, please select from one of these:")
        for name in names:
            print("\t", name)
        raise KeyError

    def __getitem__(self, keyval: str):
        return self.all()[self._get_index(keyval=keyval)]

    def __setitem__(self, keyval: str, val):
        raise NotImplementedError()


class UserWaveforms(BaseSearchContainer):
    # from maxoptics.sdk import MaxOptics
    def __init__(self, mos):
        self.mos = mos
        self._cached = []

    def all(self):
        if self._cached:
            return self._cached
        else:
            self._cached = self.mos.post(url="search_waveforms", token=self.mos.token)["result"]["result"]
            return self._cached

    def reload(self):
        self._cached = self.mos.post(url="search_waveforms", token=self.mos.token)["result"]["result"]

    def _get_index(self, keyval: str):
        names = list(map(lambda _: _["name"], list(self.all())))
        # heads = list(map(lambda _: str(re.findall("^[^\\-\\(_]+", _)[0]).strip(), names))
        # if keyval in heads:
        #     return heads.index(keyval)
        # else:
        for i, v in enumerate(names):
            if keyval == v:
                return i
        # Not Found
        print(f"Waveform {keyval} is not found, please select from one of these:")
        for name in names:
            print("\t", name)
        raise KeyError

    def __getitem__(self, keyval: str):
        return self.all()[self._get_index(keyval=keyval)]

    def __setitem__(self, keyval: str, val):
        raise NotImplementedError()
