from typing import List, Optional

import attr

from tdxapi.managers.bases import TdxManager, tdx_method
from tdxapi.models.report import Report
from tdxapi.models.report_info import ReportInfo
from tdxapi.models.report_search import ReportSearch


@attr.s
class ReportManager(TdxManager):
    @tdx_method(
        "GET",
        "/api/reports/{id}"
        "?withData={withData}&dataSortExpression={dataSortExpression}",
    )
    def get(
        self,
        report_id: int,
        with_data: Optional[bool] = False,
        data_sort_expression: Optional[str] = None,
    ) -> Report:
        """Gets information about a report, optionally including data."""
        return self.dispatcher.send(
            self.get.method,
            self.get.url.format(
                id=report_id,
                withData=with_data,
                dataSortExpression=data_sort_expression or "",
            ),
            rclass=Report,
            rlist=False,
            rpartial=False,
        )

    @tdx_method("GET", "/api/reports")
    def all(self) -> List[ReportInfo]:
        """Gets a list of all Report Builder reports visible to the user."""
        return self.dispatcher.send(
            self.all.method,
            self.all.url,
            rclass=ReportInfo,
            rlist=True,
            rpartial=True,
        )

    @tdx_method("POST", "/api/reports/search")
    def search(
        self,
        owner_uid: Optional[str] = None,
        search_text: Optional[str] = None,
        app_id: Optional[int] = None,
        app_class: Optional[str] = None,
        source_id: Optional[int] = None,
    ) -> List[ReportInfo]:
        """
        Gets a list of Report Builder reports visible to the user that match the
        provided search criteria.

        :param owner_uid: The UID of the report owner to filter on.
        :param search_text: The search text to filter on report names.
        :param app_id: The ID of the associated platform application to filter on.
        :param app_class: The system name of the application to filter on.
        :param source_id: The ID of the associated report source to filter on.
        """
        params = self._format_search_params(ReportSearch, locals())

        return self.dispatcher.send(
            self.search.method,
            self.search.url,
            data=params,
            rclass=ReportInfo,
            rlist=True,
            rpartial=True,
        )
