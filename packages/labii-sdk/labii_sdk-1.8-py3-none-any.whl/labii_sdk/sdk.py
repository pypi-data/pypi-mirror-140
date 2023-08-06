""" python api functions """
import os
import requests
from labii_sdk.api_client import APIObject

class LabiiObject:
    """ object for labii sdk """
    api = None

    def __init__(self,
        organization__sid,
        base_url="https://www.labii.dev",
        email=None,
        password=None
    ):
        self.api = APIObject(base_url=base_url, email=email, password=password, organization__sid=organization__sid)
        self.Organization = self.APIResource(self, "organizations", "organization")
        self.Application = self.APIResource(self, "organizations", "application")
        self.Subscription = self.APIResource(self, "organizations", "subscription")
        self.People = self.APIResource(self, "organizations", "personnel")
        self.Team = self.APIResource(self, "organizations", "team")
        self.OrganizationWidget = self.APIResource(self, "organizations", "organizationwidget")
        self.SAML = self.APIResource(self, "organizations", "saml")
        self.Backup = self.APIResource(self, "organizations", "backup")
        self.Project = self.APIResource(self, "projects", "project")
        self.ProjectMember = self.APIResource(self, "projects", "member")
        self.Table = self.APIResource(self, "tables", "table")
        self.Column = self.APIResource(self, "tables", "column")
        self.Section = self.APIResource(self, "tables", "section")
        self.Filter = self.APIResource(self, "tables", "filter")
        self.Record = self.APIResource(self, "tables", "row")
        self.Cell = self.APIResource(self, "tables", "cell")
        self.Version = self.APIResource(self, "tables", "version")
        self.Visitor = self.APIResource(self, "tables", "visitor")
        self.Activity = self.APIResource(self, "tables", "activity")
        self.Workflow = self.APIResource(self, "tables", "workflow")
        self.Step = self.APIResource(self, "tables", "step")
        self.Widget = self.APIResource(self, "widgets", "widget")

    class APIResource:
        """ abstract class """
        app = None
        model = None

        class Meta:
            """ meta """
            abstract = True

        def __init__(self, instance, app, model):
            """
                - instance, the outer instance
            """
            self.instance = instance
            self.app = app
            self.model = model

        def create(self, data, query=""):
            """
                Create a object
                Args:
                - data (dict), the object data
            """
            return self.instance.api.post(
                self.instance.api.get_list_url(self.app, self.model, serializer="detail", query=query),
                data
            )

        def retrieve(self, sid, query=""):
            """ Return an object """
            return self.instance.api.get(self.instance.api.get_detail_url(self.app, self.model, sid=sid, query=query))

        def list(self, page=1, page_size=10, all_pages=False, level="organization", serializer="list", query=""):
            """ Return list of objects """
            if all_pages is True:
                url = self.instance.api.get_list_url(
                    self.app,
                    self.model,
                    sid=self.instance.api.organization__sid,
                    level=level,
                    serializer=serializer,
                    query=query
                )
                return self.instance.api.get(url, True)
            # not all pages
            url = self.instance.api.get_list_url(
                self.app,
                self.model,
                sid=self.instance.api.organization__sid,
                level=level,
                serializer=serializer,
                query=f"page={page}&page_size={page_size}{'' if query == '' else '&'}{query}"
            )
            return self.instance.api.get(url)

        def modify(self, sid, data, query=""):
            """
                Change one object
                Args:
                - data (dict), the object data
            """
            return self.instance.api.patch(
                self.instance.api.get_detail_url(self.app, self.model, sid=sid, query=query),
                data
            )

        def delete(self, sid, query=""):
            """ Delete a object """
            self.instance.api.delete(self.instance.api.get_detail_url(self.app, self.model, sid=sid, query=query))

        def upload(self, sid, filename):
            """
                Upload a file for files table
                Based on files/FileUpload.js
                Need a file row to be created first
            """
            if self.app != "tables" or self.model != "row":
                raise RuntimeError("Error: 'upload' is only available for Record.")
            # step1GetPresignedPostURL
            presigned = self.instance.api.get(self.instance.api.get_detail_url(self.app, self.model, sid=sid, query="presigned_post=true"))
            # step2UploadFileToS3
            if not "presigned_post" in presigned:
                raise RuntimeError("Error: File can not be uploaded! Make sure the sid is correct and you have permission to change it.")
            data = presigned["presigned_post"]["fields"]
            file_ob = open(filename, 'rb') # pylint: disable=consider-using-with
            #data["file"] = file_ob
            response = requests.post(url=presigned["presigned_post"]["url"], data=data, files={'file': file_ob})
            # step3UpdateVersionId
            if response.status_code != 204:
                raise RuntimeError(response.text)
            file_record = self.instance.api.get(self.instance.api.get_detail_url(self.app, self.model, sid=sid))
            # update file path
            cell_path_index = [index for index, cell in enumerate(file_record["column_set"]) if cell["column"]["widget"]["sid"] == "JMPS0a40x5eLQV16afk"][0]
            file_record["column_set"][cell_path_index] = self.instance.api.patch(
                self.instance.api.get_detail_url("tables", "cell", sid=file_record["column_set"][cell_path_index]["sid"]),
                {"data": f"{presigned['presigned_post']['fields']['key'].split('?')[0]}?versionId={response.headers['x-amz-version-id']}"}
            )
            # update file size
            cell_size_index = [index for index, cell in enumerate(file_record["column_set"]) if cell["column"]["widget"]["sid"] == "KNQT0a40x5fMRW27bgl"][0]
            file_record["column_set"][cell_size_index] = self.instance.api.patch(
                self.instance.api.get_detail_url("tables", "cell", sid=file_record["column_set"][cell_size_index]["sid"]),
                {"data": os.path.getsize(filename)}
            )
            return file_record
