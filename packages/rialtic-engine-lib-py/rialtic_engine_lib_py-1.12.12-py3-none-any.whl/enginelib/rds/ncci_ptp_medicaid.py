import datetime as dt

from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.errors import Error
from enginelib.rds.client import db_client, db_name

from typing import List, Dict


class NCCIPTPMedicaid:
    @staticmethod
    def fetch_rows_in_ncci_ptp_mcd(clf: ClaimLineFocus) -> List[Dict[str, str]]:
        """
        Returns:
            list of rows in reference data set NCCI_PTP_MCD with
            the given procedureCode in column 2 and within the
            prescribed effective date range:

            EFFECTIVE_DATE <= DATE < DELETION_DATE
        """
        from_date = clf.service_period.start
        formatted_date = dt.datetime(from_date.year, from_date.month, from_date.day).strftime("%m/%d/%Y")

        query = f'''
            SELECT *
            FROM {db_name}.NCCI_PTP_MCD WHERE COLUMN_2 = '{clf.procedure_code}'
        '''

        ref_data, err = db_client.GetReferenceData(clf.request.transaction_id or 'testing', query)
        if err is not None:
            raise Error(f"Error fetching data from NCCI PTP reference data set: {err}")
        start_date = clf.service_period.start
        relevant_ref_data = []
        for entry in ref_data:
            effective_date = entry.get("effective_date", "") or "01/01/0001"
            deletion_date = entry.get("deletion_date", "") or "12/31/9999"
            if (dt.datetime.strptime(effective_date, "%m/%d/%Y").date() <= start_date
                    < dt.datetime.strptime(deletion_date, "%m/%d/%Y").date()):
                relevant_ref_data.append(entry)

        return relevant_ref_data or list()
