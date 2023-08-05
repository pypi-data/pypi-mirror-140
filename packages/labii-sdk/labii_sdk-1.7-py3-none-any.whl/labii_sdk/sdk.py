""" python api functions """
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
