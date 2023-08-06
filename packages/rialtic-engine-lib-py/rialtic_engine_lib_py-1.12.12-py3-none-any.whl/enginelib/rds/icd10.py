from enum import Enum
from typing import Dict, List, Tuple, Set
import datetime as dt
import re

from enginelib.errors import Error
from enginelib.rds.client import db_client, db_name

class CodeType(Enum):
    valid = "valid"
    deleted = "deleted"
    incomplete = "incomplete"


class ICD10:
    def __init__(self, service_date: dt.date):
        self.icd10_hash: Dict[str, Dict[str, str]] = dict()
        self.service_date: dt.date = service_date

    def __contains__(self, code: str):
        return self.is_present(code)

    def code_info(self, code: str) -> Dict[str, str]:
        formatted_code = code.replace(".", "")
        if code not in self.icd10_hash:
            self.icd10_hash[code] = self._fetch_code_info(formatted_code, self.service_date)

        return self.icd10_hash[code]

    @staticmethod
    def _fetch_code_info(code: str, service_date: dt.date) -> Dict[str, str]:
        """If 'code' is in the ICD10 dataset pertaining the effective date of the CUE and with the appropriate code type,
        and if the DB query was successful, this function returns a non-empty
        dictionary with the information of the given ICD10 code.
        If the DB query was not successful, this function raises a DataError.
        If the DB query was successful, but the code was not in the DB, this
        function returns an empty dictionary."""

        # The validity period of an icd10 dataset for a given year goes from OCT 1 of the previous year
        # to SEP 30 of the next
        # So the validity period of the 2022 dataset goes from OCT 1 2021 to SEP 30 2022
        year = service_date.year
        if service_date >= dt.date(year, 8, 1):
            year = year + 1

        table_name = f"icd10_{year}" if year is not None else "icd10"
        # noinspection SqlResolve
        query = f'''
        SELECT *
        FROM {db_name}.{table_name}
        WHERE "code"='{code}';
        '''

        ref_data, err = db_client.GetReferenceData("multi_policy_prefilter", query)
        if err:
            raise Error(f'Not able to access ICD10 reference data: {err}.')
        try:
            if ref_data is None or not isinstance(ref_data, list) or len(ref_data) == 0:
                return dict()
            return ref_data[0]
        except (IndexError, KeyError, TypeError):
            raise Error(f'Not able to access ICD10 reference data to fetch description for code {code}.')

    def is_present(self, code: str) -> bool:
        code_info = self.code_info(code)
        return bool(code_info)

    def in_range(self, code: str, code_min: str, code_max: str) -> bool:
        """The comparison below is alphanumeric (i.e. string)."""
        try:
            return code_min <= code <= code_max and self.is_present(code)
        except TypeError:
            raise Error(f"Either the code minimum: {code_min} or the code maximum: {code_max} "
                        f"is not a string.")


class ICD10Collection:
    def __init__(self, service_date: dt.date, icd_list_of_codes_and_ranges: str):
        self.icd10_instance = ICD10(service_date)
        self.ranges, self.codes = self._process_list_of_codes_and_ranges(icd_list_of_codes_and_ranges)

    def __contains__(self, code: str) -> bool:
        if code in self.codes:
            return True
        for _range in self.ranges:
            min_c, max_c = _range.split("-")
            if self.icd10_instance.in_range(code, min_c, max_c):
                return True
        return False

    @staticmethod
    def _process_list_of_codes_and_ranges(icd_list_of_codes_and_ranges: str = "") -> Tuple[Set[str], Set[str]]:
        normalized_icd_list = icd_list_of_codes_and_ranges.replace(',', '|')
        ranges = {item.strip() for item in normalized_icd_list.split('|') if "-" in item}
        codes = {item.strip() for item in normalized_icd_list.split('|') if "-" not in item}
        return ranges, codes


class ICD10_DX10:
    @staticmethod
    def query_dx_codes(codes: List[str], start_date: dt.date, transaction_id: str) -> Dict[str, Dict]:
        code_set = ", ".join(f"'{_sql_sanitize(x)}'" for x in codes)
        # noinspection SqlResolve,SqlDialectInspection,SqlNoDataSourceInspection
        query = f'''
            SELECT *
            FROM {db_name}.icd10_dx10
            WHERE diagnosis IN ({code_set});
        '''
        records, err = db_client.GetReferenceData(transactionId=transaction_id, query=query)
        if err:
            raise Error(f"Unable to query ICD-10 DX10 Data, error: {str(err)}")
        return {rec['diagnosis']: rec for rec in (records or []) if
                rec['effective_start_date'] <= start_date.strftime("%Y-%m-%d") < str(rec['effective_end_date'])}

_bad_chars = re.compile(r'[^0-9a-zA-z\-_]')
def _sql_sanitize(text: str) -> str:
    return _bad_chars.sub("", text)