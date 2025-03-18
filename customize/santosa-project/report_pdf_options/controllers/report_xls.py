# -*- coding: utf-8 -*-

import json
import logging

from werkzeug.urls import url_decode

from odoo.http import (
    content_disposition,
    request,
    route,
)
from odoo.http import (
    serialize_exception as _serialize_exception,
)
from odoo.tools import html_escape
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.web.controllers.report import ReportController


class ReportXls(ReportController):

    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == "xlsx":
            report = request.env["ir.actions.report"]._get_report_from_name(reportname)
            context = dict(request.env.context)
            if docids:
                docids = [int(i) for i in docids.split(",")]
            if data.get("options"):
                data.update(json.loads(data.pop("options")))
            if data.get("context"):
                data["context"] = json.loads(data["context"])
                context.update(data["context"])
            xlsx = report.with_context(**context)._render_xlsx(
                reportname, docids, data=data
            )[0]
            xlsxhttpheaders = [
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet",
                ),
                ("Content-Length", len(xlsx)),
            ]
            return request.make_response(xlsx, headers=xlsxhttpheaders)
        return super().report_routes(reportname, docids, converter, **data)