from datetime import datetime
from re import T
from pathlib import Path
import click
import efemarai as ef
from rich.console import Console
from rich.table import Table


console = Console()


@click.group()
def main():
    """Efemarai CLI."""
    pass


@main.command()
@click.option("-c", "--config", help="Optional configuration file.")
def init(config):
    """Initialize Efemarai."""
    ef.Session()._user_setup(config_file=config)


@main.group()
def project():
    """Manage projects."""
    pass


@project.command("create")
@click.argument("config", required=True)
@click.option(
    "--exists_ok", default=False, help="Append differences if project already exists."
)
def project_create(config, exists_ok):
    """Create a project following the specified configuration file.

    CONFIG - configuration file."""
    result = ef.Session().load(config, exists_ok=exists_ok)
    print(result)


@project.command("list")
def project_list():
    """Lists the projects associated with the current user."""
    table = Table(box=None)
    [table.add_column(x) for x in ["Id", "Name", "Problem Type"]]
    for m in ef.Session().projects:
        table.add_row(m.id, m.name, str(m.problem_type))
    console.print(table)


@main.group()
def model():
    """Manage models."""
    pass


@model.command("list")
def model_list():
    """Lists the models in the current project."""
    project = _get_project()
    if not project:
        return

    table = Table(box=None)
    [table.add_column(x) for x in ["Id", "Name"]]
    for m in project.models:
        table.add_row(m.id, m.name)
    console.print(table)


@model.command("create")
@click.argument("config", required=True)
def model_create(config):
    """Create a model in the current project.

    CONFIG - configuration file."""
    project = _get_project()
    if not project:
        return
    config_file = ef.Session._read_config(config)
    model = project.create_model(**config_file["model"])
    return model


@model.command("delete")
@click.argument("model", required=True)
def model_delete(model):
    """Delete a model from the current project.

    MODEL - the name or ID of the model."""
    project = _get_project()
    if not project:
        return

    if _check_for_multiple_entities(project.models, model):
        console.print("There are multiple models with the given:\n")
        models = [t for t in project.models if t.name == test]
        _print_table(models)
        console.print(
            f"\nRun the command with a specific model id: [bold green]$ efemarai model delete {models[0].id}",
        )
        return

    model = project.model(model)
    model.delete()


@main.group()
def domain():
    """Manage domains."""
    pass


@domain.command("list")
def domain_list():
    """Lists the domains in the current project."""
    project = _get_project()
    if not project:
        return

    table = Table(box=None)
    [table.add_column(x) for x in ["Id", "Name"]]
    for d in project.domains:
        table.add_row(d.id, d.name)
    console.print(table)


@domain.command("create")
@click.argument("config", required=True)
def domain_create(config):
    """Create a domain in the current project.

    CONFIG - configuration file."""
    project = _get_project()
    if not project:
        return
    config_file = ef.Session._read_config(config)
    domain = project.create_domain(**config_file["domain"])
    return domain


@domain.command("delete")
@click.argument("domain", required=True)
def domain_delete(domain):
    """Delete a domain from the current project.

    DOMAIN - the name or ID of the domain."""
    project = _get_project()
    if not project:
        return

    if _check_for_multiple_entities(project.domains, domain):
        console.print("There are multiple domains with the given name:\n")
        domains = [t for t in project.domains if t.name == test]
        _print_table(domains)
        console.print(
            f"\nRun the command with a specific domain id: [bold green]$ efemarai domain delete {domains[0].id}",
        )
        return

    domain = project.domain(domain)
    domain.delete()


@domain.command("download")
@click.argument("domain", required=True)
@click.option("-o", "--output", default=None, help="Optional domain output file.")
def domain_download(domain, output):
    """Download a domain.

    DOMAIN - the name of the domain."""
    project = _get_project()
    if not project:
        return

    domain = project.domain(domain)
    filename = domain.download(filename=output)
    console.print(
        (f":heavy_check_mark: Downloaded '{domain.name}' reports to: \n  {filename}"),
        style="green",
    )


@main.group()
def dataset():
    """Manage datasets."""
    pass


@dataset.command("list")
def dataset_list():
    """Lists the datasets in the current project."""
    project = _get_project()
    if not project:
        return

    table = Table(box=None)
    [table.add_column(x) for x in ["Id", "Name", "Loaded"]]
    for d in project.datasets:
        table.add_row(d.id, d.name, str(d.loaded))
    console.print(table)


@dataset.command("create")
@click.argument("config", required=True)
def dataset_create(config):
    """Create a dataset in the current project.

    CONFIG - configuration file."""
    project = _get_project()
    if not project:
        return
    config_file = ef.Session._read_config(config)
    dataset = project.create_dataset(**config_file["dataset"])
    return dataset


@dataset.command("delete")
@click.argument("dataset", required=True)
def dataset_delete(dataset):
    """Delete a dataset from the current project.

    DATASET - the name or ID of the dataset."""
    project = _get_project()
    if not project:
        return

    if _check_for_multiple_entities(project.datasets, dataset):
        console.print("There are multiple datasets with the given name:\n")
        datasets = [t for t in project.datasets if t.name == test]
        _print_table(datasets)
        console.print(
            f"\nRun the command with a specific dataset id: [bold green]$ efemarai dataset delete {datasets[0].id}",
        )
        return

    dataset = project.dataset(dataset)
    dataset.delete()


@main.group()
def test():
    """Manage stress tests."""
    pass


@test.command("list")
def test_list():
    """Lists the stress tests in the current project."""
    project = _get_project()
    if not project:
        return

    _print_table(project.stress_tests)


@test.command("run")
@click.argument("config", required=True)
def test_run(config):
    """Run a stress test.

    CONFIG - stress test configuration file."""
    project = _get_project()
    if not project:
        return

    config_file = ef.Session._read_config(config)
    test = project.create_stress_test(**config_file["test"])
    cfg = ef.Session._read_config()
    console.print(f"{cfg['url']}project/{project.id}/runs/{test.id}")


@test.command("delete")
@click.argument("test", required=True)
def test_delete(test):
    """Delete a stress test from the current project.

    TEST - the name or ID of the stress test."""
    project = _get_project()
    if not project:
        return

    if _check_for_multiple_entities(project.stress_tests, test):
        console.print("There are multiple stress tests with the given name:\n")
        tests = [t for t in project.stress_tests if t.name == test]
        _print_table(tests)
        console.print(
            f"\nRun the command with a specific stress test id: [bold green]$ efemarai test delete {tests[0].id}",
        )
        return

    test = project.stress_test(test)
    test.delete()


@test.command("download")
@click.argument("test", required=True)
@click.option("--min_score", default=0, help="Minimum score for the samples.")
@click.option("--include_dataset", default=False, help="Include original test dataset.")
@click.option("--path", default=None, help="Path to the downloaded files.")
@click.option("--unzip", default=True, help="Whether to unzip the resulting file.")
@click.option("--ignore_cache", default=False, help="Ignore local cache.")
def test_download(test, min_score, include_dataset, path, unzip, ignore_cache):
    """Download the stress test vulnerabilities dataset.

    TEST - the name or ID of the stress test to download."""
    project = _get_project()
    if not project:
        return

    test = project.stress_test(test)
    test.vulnerabilities_dataset(
        min_score=min_score,
        include_dataset=include_dataset,
        path=path,
        unzip=unzip,
        ignore_cache=ignore_cache,
    )


@test.command("reports")
@click.argument("test", required=True)
@click.option("-o", "--output", default=None, help="Optional output file.")
def test_reports(test, output):
    """Export the stress test reports.

    TEST - name or ID of the stress test."""
    project = _get_project()
    if not project:
        return

    test = project.stress_test(test)
    filename = test.download_reports(filename=output)
    console.print(
        (f":heavy_check_mark: Downloaded '{test.name}' reports to: \n  {filename}"),
        style="green",
    )


def _print_table(tests):
    table = Table(box=None)
    [table.add_column(x) for x in ["Id", "Name", "Model", "Dataset", "Domain", "State"]]
    for t in tests:
        table.add_row(
            t.id, t.name, t.model.name, t.dataset.name, t.domain.name, str(t.state)
        )
    console.print(table)


def _check_for_multiple_entities(entities, name):
    length = len(list(filter(lambda x: x.name == name, entities)))
    return length > 1


def _get_project():
    if not Path("efemarai.yaml").is_file():
        console.print(
            f":poop: Cannot find 'efemarai.yaml' in the current directory.", style="red"
        )
        exit(1)

    ef_file = ef.Session()._load_config_file("efemarai.yaml")
    if "project" in ef_file and "name" in ef_file["project"]:
        name = ef_file["project"]["name"]
        project = ef.Session().project(name)
        if not project:
            console.print(f"Project '{name}' is not existing.")
            return

        return project

    console.print(
        f":poop: 'efemarai.yaml' file not configured properly (does not container project and name within).",
        style="red",
    )
    exit(1)


if __name__ == "__main__":
    main()
