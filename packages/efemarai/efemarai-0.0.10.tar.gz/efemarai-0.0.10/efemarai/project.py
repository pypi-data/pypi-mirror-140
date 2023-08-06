from efemarai.dataset import Dataset
from efemarai.domain import Domain
from efemarai.model import Model, ModelParams, ModelRepository
from efemarai.problem_type import ProblemType
from efemarai.stress_test import StressTest


class Project:
    """Provides project related functionality."""

    @staticmethod
    def create(session, name, description, problem_type, exists_ok=False):
        if name is None or not ProblemType.has(problem_type):
            return None

        existing_project = next((p for p in session.projects if p.name == name), None)
        if existing_project:
            if exists_ok:
                return existing_project
            else:
                raise ValueError(f"Project {name} already exists and exists_ok=False.")

        response = session._put(
            "api/project",
            json={
                "name": name,
                "description": description,
                "problem_type": problem_type,
            },
        )
        return Project(session, response["id"], name, description, problem_type)

    def __init__(self, session, id, name, description, problem_type):
        self._session = session
        self.id = id
        self.name = name
        self.description = description
        self.problem_type = ProblemType(problem_type)

    def __repr__(self):
        res = f"{self.__module__}.{self.__class__.__name__}("
        res += f"\n  id={self.id}"
        res += f"\n  name={self.name}"
        res += f"\n  description={self.description}"
        res += f"\n  problem_type={self.problem_type}"
        res += f"\n)"
        return res

    @property
    def models(self):
        """Returns a list of the models associated with the project."""

        return [
            Model(
                self,
                model["id"],
                model["name"],
                repository=ModelRepository(
                    url=model["repository_url"],
                    branch=model["branch"],
                    access_token=model["access_token"],
                ),
                params=ModelParams(url=model["model_url"]),
            )
            for model in self._session._get(f"api/models/{self.id}")
        ]

    def model(self, name):
        """Returns the model specified by the name."""

        model = next((m for m in self.models if m.name == name), None)
        return model

    def create_model(
        self, name, repository=None, params=None, exists_ok=False, **kwargs
    ):
        """Creates a model."""

        existing_model = next((m for m in self.models if m.name == name), None)
        if existing_model:
            if exists_ok:
                return existing_model
            else:
                raise ValueError(f"Model {name} already exists and exists_ok=False.")

        model = Model.create(self, name, repository, params)
        return model

    @property
    def datasets(self):
        """Returns a list of the datasets associated with the project."""

        return [
            Dataset(
                self,
                dataset["id"],
                dataset["name"],
                dataset["format"],
                dataset["stage"],
                dataset["data_url"],
                dataset["annotations_url"],
                dataset["loaded"],
                Dataset._parse_classes(dataset["classes"]),
            )
            for dataset in self._session._get(f"api/datasets/{self.id}")
        ]

    def dataset(self, name):
        """Returns the dataset specified by the name."""

        dataset = next((d for d in self.datasets if d.name == name), None)
        return dataset

    def create_dataset(
        self,
        name,
        format=None,
        stage=None,
        data_url=None,
        annotations_url=None,
        credentials=None,
        upload=False,
        num_datapoints=None,
        mask_generation=None,
        exists_ok=False,
        **kwargs,
    ):
        """Creates a dataset."""

        existing_dataset = next((d for d in self.datasets if d.name == name), None)
        if existing_dataset:
            if exists_ok:
                return existing_dataset
            else:
                raise ValueError(f"Dataset {name} already exists and exists_ok=False.")

        dataset = Dataset.create(
            self,
            name,
            format,
            stage,
            data_url,
            annotations_url,
            credentials,
            upload,
            num_datapoints,
            mask_generation,
        )

        return dataset

    @property
    def domains(self):
        """Returns a list of the domains associated with the project."""

        return [
            Domain(
                self,
                domain["id"],
                domain["name"],
                domain["transformations"],
                domain["graph"],
            )
            for domain in self._session._get(f"api/domains/{self.id}")
        ]

    def domain(self, name):
        """Returns the domain specified by the name."""

        domain = next((d for d in self.domains if d.name == name), None)
        return domain

    def create_domain(
        self, name, transformations=None, graph=None, exists_ok=False, **kwargs
    ):
        """Creates a domain."""

        existing_domain = next((d for d in self.domains if d.name == name), None)
        if existing_domain:
            if exists_ok:
                return existing_domain
            else:
                raise ValueError(f"Domain {name} already exists and exists_ok=False.")

        domain = Domain.create(self, name, transformations, graph)
        return domain

    @property
    def stress_tests(self):
        """Returns a list of the stress tests associated with the project."""

        return [
            StressTest(
                self,
                test["id"],
                test["name"],
                test["model"]["id"],
                test["domain"]["id"],
                test["dataset"]["id"],
                test["states"][-1]["name"],
                test["reports"],
            )
            for test in self._session._get(f"api/getRuns/{self.id}")["objects"]
        ]

    def stress_test(self, name):
        """Returns the stress test specified by the name."""

        test = next((t for t in self.stress_tests if t.name == name), None)
        return test

    def create_stress_test(
        self,
        name,
        model=None,
        domain=None,
        dataset=None,
        num_samples=None,
        num_runs=None,
        concurrent_runs=None,
        **kwargs,
    ):
        """Creates a stress test."""

        test = StressTest.create(
            self,
            name,
            model,
            domain,
            dataset,
            num_samples,
            num_runs,
            concurrent_runs,
        )

        return test

    def delete(self):
        """Deletes a project, including the domains, datasets and models."""

        for domain in self.domains:
            domain.delete()

        for dataset in self.datasets:
            dataset.delete()

        for model in self.models:
            model.delete()

        self._session._delete(f"api/project/{self.id}")
