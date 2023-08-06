import time
from functools import wraps
from enum import Enum

class ParseOption(Enum):
    DICT = 'dict'
    ETREE = 'etree'
    XML = 'xml'

def parse_xml_return(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        parse_opt = kwargs.pop('parse_opt', ParseOption.DICT)
        include_resp = kwargs.pop('include_resp', False)
        assert isinstance(parse_opt, (ParseOption, str)), 'parse_opt must be an instance of str or ParseOption'
        if isinstance(parse_opt, str):
            parse_opt = ParseOption(parse_opt)

        # retries in case of Nomadix auth backoff
        http_response = None
        for _ in range(3):
            http_response = func(self, *args, **kwargs)
            if 200 <= http_response.status_code < 300:
                break
            time.sleep(1)
        if http_response is None:
            raise Exception('Could not get response from Nomadix GW')

        parsed_xml = http_response.text
        if parse_opt is ParseOption.DICT:
            parsed_xml = self.parse_xml_to_dict(http_response.text)
        elif parse_opt is ParseOption.ETREE:
            parsed_xml = self.parse_xml_to_etree(http_response.text)
        elif parse_opt is ParseOption.XML:
            parsed_xml = self.xml_treat_raw(http_response.text)
        else:
            # FIXME: Did not find parse method
            # log error
            pass

        if include_resp:
            return parsed_xml, http_response
        return parsed_xml
    return wrapper
