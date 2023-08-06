import os
import zipfile

from enum import Enum
from time import sleep

import boto3
from appdirs import user_data_dir
from botocore.errorfactory import ClientError

from rich.console import Console
from rich.prompt import Confirm, Prompt

from efemarai.problem_type import ProblemType


console = Console()


class TestRunState(Enum):
    NotStarted = "NotStarted"
    GeneratingBaselines = "GeneratingBaselines"
    Starting = "Starting"
    Running = "Running"
    GeneratingReport = "Generating Report"
    Finished = "Finished"
    Failed = "Failed"


class StressTest:
    @staticmethod
    def create(
        project,
        name,
        model,
        domain,
        dataset,
        num_samples=50,
        num_runs=1,
        concurrent_runs=1,
    ):
        """Create a stress test."""

        if isinstance(model, str):
            model = project.model(model)

        if isinstance(dataset, str):
            dataset = project.dataset(dataset)

        if isinstance(domain, str):
            domain = project.domain(domain)

        if num_samples is None:
            num_samples = 50

        if num_runs is None:
            num_runs = 1

        if concurrent_runs is None:
            concurrent_runs = 1

        response = project._session._post(
            "api/runTest",
            json={
                "name": name,
                "model": model.id,
                "dataset": dataset.id,
                "domain": domain.id,
                "project": project.id,
                "samples_per_run": num_samples,
                "runs_count": num_runs,
                "concurrent_runs": concurrent_runs,
            },
        )
        return StressTest(
            project,
            response["id"],
            name,
            model,
            domain,
            dataset,
            "NotStarted",
            {},
        )

    def __init__(self, project, id, name, model, domain, dataset, state, reports):
        self.project = project
        self.id = id
        self.name = name

        if isinstance(model, str):
            self._model = None
            self._model_id = model
        else:
            self._model = model
            self._model_id = model.id

        if isinstance(domain, str):
            self._domain = None
            self._domain_id = domain
        else:
            self._domain = domain
            self._domain_id = domain.id

        if isinstance(dataset, str):
            self._dataset = None
            self._dataset_id = dataset
        else:
            self._dataset = dataset
            self._dataset_id = dataset.id

        self.state = TestRunState(state)
        self._reports = reports

    def __repr__(self):
        res = f"{self.__module__}.{self.__class__.__name__}("
        res += f"\n  id={self.id}"
        res += f"\n  name={self.name}"
        res += f"\n  model={self.model.name}"
        res += f"\n  domain={self.domain.name}"
        res += f"\n  dataset={self.dataset.name}"
        res += f"\n  state={self.state}"
        res += f"\n  len(reports)={len(self.reports)}"
        res += f"\n)"
        return res

    @property
    def reports(self):
        if not self._reports:
            response = self.project._session._get(
                "api/getTestRun", params={"testRunId": self.id}
            )
            self._reports = response["reports"]

        return self._reports

    @property
    def model(self):
        """Returns the model associated with the stress test."""

        if self._model is None:
            self._model = next(m for m in self.project.models if m.id == self._model_id)
        return self._model

    @property
    def domain(self):
        """Returns the domain associated with the stress test."""

        if self._domain is None:
            self._domain = next(
                d for d in self.project.domains if d.id == self._domain_id
            )
        return self._domain

    @property
    def dataset(self):
        """Returns the dataset associated with the stress test."""

        if self._dataset is None:
            self._dataset = next(
                d for d in self.project.datasets if d.id == self._dataset_id
            )
        return self._dataset

    @property
    def finished(self):
        """Retuns if the stress test has sucessfully finished."""

        return self.state == TestRunState.Finished

    @property
    def failed(self):
        """Retuns if the stress test has failed."""

        return self.state == TestRunState.Failed

    @property
    def running(self):
        """Retuns if the stress test is still running - not failed or finished."""

        return self.state != TestRunState.Finished and self.state != TestRunState.Failed

    def reload(self):
        """Reloads the stress test from the remote endpoint."""

        response = self.project._session._get(
                "api/getTestRun", params={"testRunId": self.id}
            )
        self.state = response["state"]
        self.reports = response["reports"]

        return self

    def vulnerabilities_dataset(
        self,
        min_score=0.0,
        include_dataset=False,
        path=None,
        unzip=True,
        ignore_cache=False,
    ):
        """Returns the vulnerabilities dataset associated with the stress test."""

        if not self.finished:
            console.print(
                (
                    ":warning: Cannot export vulnerabilities "
                    "dataset as stress test is still running"
                ),
                style="yellow",
            )
            return None

        if path is None:
            path = user_data_dir(appname="efemarai")

        path = os.path.join(path, self.id)

        export_format = None
        if self.project.problem_type == ProblemType.Classification:
            export_format = "imagenet"
        elif self.project.problem_type == ProblemType.ObjectDetection:
            export_format = "coco"
        elif self.project.problem_type == ProblemType.InstanceSegmentation:
            export_format = "coco"

        if export_format is None:
            console.print(":poop: Unsupported problem type.", style="red")
            return None

        if not ignore_cache:
            name = "vulnerabilities_dataset"
            name += f"_{export_format}_{include_dataset}_{min_score:.3f}"
            cache_name = os.path.join(path, name)
            if os.path.exists(cache_name) or os.path.exists(cache_name + ".zip"):
                return cache_name

        access = self.project._session._post(
            "api/exportDataset",
            json={
                "id": self.id,
                "format": export_format,
                "merge": include_dataset,
                "min_score": min_score,
                "async_download": True,
            },
        )

        s3 = boto3.client(
            "s3",
            aws_access_key_id=access["AccessKeyId"],
            aws_secret_access_key=access["SecretAccessKey"],
            aws_session_token=access["SessionToken"],
            endpoint_url=access["Url"],
        )

        with console.status(f"Generating '{self.name}' vulnerabilities dataset"):
            while True:
                try:
                    response = s3.head_object(
                        Bucket=access["Bucket"], Key=access["ObjectKey"]
                    )
                    size = response["ContentLength"]
                    break
                except ClientError:
                    sleep(1)

        with self.project._session._progress_bar() as progress:
            task = progress.add_task(f"Downloading dataset ", total=float(size))
            callback = lambda num_bytes: progress.advance(task, num_bytes)

            os.makedirs(path, exist_ok=True)
            filename = os.path.join(path, os.path.basename(access["ObjectKey"]))

            s3.download_file(
                access["Bucket"], access["ObjectKey"], filename, Callback=callback
            )

        if unzip:
            with console.status(f"Unzipping dataset"):
                dirname = os.path.splitext(filename)[0]
                with zipfile.ZipFile(filename, "r") as f:
                    f.extractall(dirname)

                os.remove(filename)

                filename = dirname

        console.print(
            (
                f":heavy_check_mark: Downloaded '{self.name}' "
                f"vulnerabilities dataset to \n  {filename}"
            ),
            style="green",
        )

        return filename
