import re
import yaml
import numbers


class Domain:
    @staticmethod
    def create(project, name, transformations, graph):
        if name is None or name is None or transformations is None or graph is None:
            return None

        session = project._session
        response = session._put(
            f"api/domain/undefined/{project.id}",
            json={"name": name, "projectId": project.id},
        )
        domain_id = response["id"]

        response = session._put(
            f"api/domain/{domain_id}/import-flow",
            json={
                "transformations": transformations,
                "graph": graph,
            },
        )

        return Domain(
            project, domain_id, name, response["transformations"], response["graph"]
        )

    def __init__(self, project, id, name, transformations, graph):
        self.project = project
        self.id = id
        self.name = name
        self.transformations = transformations
        self.graph = graph

    def __repr__(self):
        res = f"{self.__module__}.{self.__class__.__name__}("
        res += f"\n  id={self.id}"
        res += f"\n  name={self.name}"
        res += f"\n  transformations={self.transformations}"
        res += f"\n  graph={self.graph}"
        res += f"\n)"
        return res

    def download(self, filename=None):
        if filename is None:
            # Remove non-ascii and non-alphanumeric characters
            filename = re.sub(r"[^A-Za-z0-9 ]", r"", self.name)
            # Collapse repeating spaces
            filename = re.sub(r"  +", r" ", filename)
            # Replace spaces with dashes and convert to lowercase
            filename = filename.replace(" ", "_").lower()
            filename += ".yaml"

        response = self.project._session._get(f"api/domain/{self.id}/export")
        with open(filename, "w") as f:
            f.write(response["definition"])

        return filename

    def delete(self):
        self.project._session._delete(f"api/domain/{self.id}/{self.project.id}")
