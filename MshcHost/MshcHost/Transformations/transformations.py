from typing import Dict
from re import finditer


class Transformation():
    def Transform(self, reponse: str) -> str:
        raise NotImplementedError()


class HrefTransformation(Transformation):
    regex_string = 'href="(ms-xhelp:///\?id=(.*?))"'

    def __init__(self, index: Dict[str, str]):
        self.index = index

    def Transform(self, response: str) -> str:
        matches = finditer(self.regex_string, response)
        for match in matches:
            matched_id = match.group(2)
            response = response.replace(
                match.group(1), self.index.get(matched_id, "#"))
        return response
