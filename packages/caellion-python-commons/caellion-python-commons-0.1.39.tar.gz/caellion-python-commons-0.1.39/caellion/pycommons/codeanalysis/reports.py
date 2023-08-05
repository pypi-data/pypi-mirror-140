"""!
This module provides utlilities related to creating Jenkins' warnings-ng-plugin-compatible reports from codeanalysis
"""

import json
import re


class ReportBuilder:
    """!
    This class provides a set of methods to create reports that are compatible with Jenkins' warnings-ng plugin
    """

    issues_all = None

    def __init__(self):
        """!
        Initialize the ReportBuilder
        """
        if self.issues_all is None:
            self.issues_all = {"_class": "io.jenkins.plugins.analysis.core.restapi.ReportApi", "issues": [], "size": 0}
        else:
            raise ValueError("Could not initialize the ReportBuilder, because its 'issues_all' property was not None.")

    def extract_basename_file(self, path):
        """!
        Extracts basename of a given path (only files). Should Work with any OS Path on any OS

        @param path path to get base folder path of
        @returns base folder path
        """
        basename = re.search(r"[^\\/]+(?![\\/])$", path)
        if basename:
            return basename.group(0)

    def addIssue(self, path, severity, message, lineStart=-1, lineEnd=-1, columnStart=-1, columnEnd=-1, category=None, type=None, description=None, packageName=None, moduleName=None, additionalProperties=None):
        """!
        Adds a new issue to the report

        @warning This function will not add duplicate issue to the report

        @param path path to the file in which the issue happens
        @param severity severity level for the issue, allowed options are LOW, NORMAL, HIGH, CRITICAL or ERROR
        @param message issue message (brief description of the problem)
        @param lineStart line at which issue happens or starting line of a block in which it happens
        @param lineEnd ending line of a block in which issue hapens
        @param columnStart column at which issue happens or starting column of a block in which it happens
        @param columnEnd ending column of a block in which issue happens
        @param category issue category to show in jenkins
        @param type issue type to show in jenkins
        @param description issue description (longer and more precise than message)
        @param packageName fully qualified name of the package in which the issue happens
        @param moduleName fully qualifies name of the module in which the issue happens
        @param additionalProperties additional parameters to pass to Jenkins' warnings-ng plugin
        """
        lineStart = int(lineStart)
        lineEnd = int(lineEnd)
        columnStart = int(columnStart)
        columnEnd = int(columnEnd)

        filename = self.extract_basename_file(path)
        severity = severity.upper()
        if filename is None or filename == "":
            raise Exception("Path is not a file path!")
        if severity not in ["LOW", "NORMAL", "HIGH", "CRITICAL", "ERROR"]:
            raise Exception("Path is not a file path!")
        if message is None or message == "":
            raise Exception("Message must not be empty!")
        dirname = path.replace(filename, "")

        issue = {"fileName": path, "directory": dirname, "severity": severity, "message": message}

        if lineStart > -1:
            issue.update({"lineStart": lineStart})

        if lineStart > -1 and lineEnd > -1:  # requires start to have end
            issue.update({"lineEnd": lineEnd})

        if columnStart > -1:
            issue.update({"columnStart": columnStart})

        if columnStart > -1 and columnEnd > -1:  # requires start to have end
            issue.update({"columnEnd": columnEnd})

        if category is not None:
            issue.update({"category": category})

        if type is not None:
            issue.update({"type": type})

        if description is not None:
            issue.update({"description": description})

        if packageName is not None:
            issue.update({"packageName": packageName})

        if moduleName is not None:
            issue.update({"moduleName": moduleName})

        if additionalProperties is not None:
            issue.update({"additionalProperties": additionalProperties})

        if issue not in self.issues_all["issues"]:
            self.issues_all["issues"].append(issue)

    def generateReport(self):
        """!
        Generates the report in json format

        @returns json-formatted dictionary containing all issues and _class header
        """
        self.issues_all["size"] = len(self.issues_all["issues"])
        return json.dumps(self.issues_all)
