import re

from typing import List, Dict, Union

from enginelib.rds.client import db_client, db_name
from enginelib.errors import Error
from functools import lru_cache


class DrugsAndBiologicals:

    @staticmethod
    def get_body_surface_dosed_data(drug_code: str, ndc_code: str, transaction_id: str) -> list:
        query = f'''
        SELECT "dxcode", "hcpcsconversion", "drugcode", "redlevel", "yellowlevela", "yellowlevelb", "greenlevela", "greenlevelb", "muot", "timeperiod", "timeperioduom", "mfot", "ptagemin", "ptageminuom", "ptagemax", "ptagemaxuom", "redlevelaverage", "yellowlevelaaverage", "yellowlevelbaverage", "greenlevelaaverage", "greenlevelbaverage", "doseunitofmeasure", "singleormultidose", "dailymaximumunitsround", "dailymaximumunits"
        FROM {db_name}.body_surface_dosed
        WHERE "drugcode"='{drug_code}' AND "associatedndcs"='{ndc_code}'
        '''

        refdata, err = db_client.GetReferenceData(transaction_id, query)

        if err:
            raise Error(err)

        if refdata:
            return [
                {key: str(value) for key, value in row.items()}
                for row in refdata
            ]
        return []

    @staticmethod
    def get_weight_dosed_data(drug_code: str, ndc_code: str, transaction_id: str) -> list:
        query = f'''
        SELECT "dxcode", "hcpcsconversion", "drugcode", "redlevel", "yellowlevela", "yellowlevelb", "greenlevela", "greenlevelb", "muot", "timeperiod", "timeperioduom", "mfot", "ptagemin", "ptageminuom", "ptagemax", "ptagemaxuom", "redlevelaverage", "yellowlevelaaverage", "yellowlevelbaverage", "greenlevelaaverage", "greenlevelbaverage", "doseunitofmeasure", "singleormultidose", "dailymaximumunitsround", "dailymaximumunits"
        FROM {db_name}.weight_dosed
        WHERE "drugcode"='{drug_code}' AND "associatedndcs"='{ndc_code}'
        '''

        refdata, err = db_client.GetReferenceData(transaction_id, query)

        if err:
            raise Error(err)

        if refdata:
            return [
                {key: str(value) for key, value in row.items()}
                for row in refdata
            ]
        return []

    @staticmethod
    @lru_cache()
    def get_static_dosed_data(drug_code: str) -> Union[List[Dict], None]:
        # sanitization check
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9]{2}(\.[a-zA-Z0-9]{0,4})?", drug_code):
            return None

        query = '''
                        SELECT * FROM {}.static_dosed WHERE "drugcode"='{}'
                    '''.format(db_name, drug_code)
        reference_data, err = db_client.GetReferenceData("testTransactionID", query)
        if err or reference_data is None:
            return None
        return reference_data
