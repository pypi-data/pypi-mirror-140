import docker
import typer

from pathlib import Path

from . import COMPONENTS
from .utils import ask_user_about_environment, env_variables, subprocess_cmd_to_str


class ComponentRunner:
    """This class is used to run the components of the project by the cli."""
    def __init__(self) -> None:
        """
        Initialize the Runner class that will run the components.
        """
        self.client = docker.from_env()
        self.available_services = COMPONENTS

    
    def __call__(self, service: str):
        """
        Call the run function.

        Parameters
        ----------
        service: str
            Service to run.
        """
        return self.run(service)

    
    def run(self, service: str) -> bool:
        """
        Function that will run the service passed as argument.

        Parameters
        ----------
        service: str
            Service to run.
        
        Returns
        -------
        bool
            True if the service exists, raises an error otherwise.
        """
        self._check_service(service)
        
        if service == "interface":
            self._run_interface()
        elif service == "serving":
            self._run_serving()
        elif service == "training":
            ask_user_about_environment()
            self._run_training()
        return True

    
    def _check_service(self, service: str) -> bool:
        """
        Check if the service exists in the available services.

        Parameters
        ----------
        service: str
            Service to check.
        
        Returns
        -------
        bool
            True if the service exists, raises an error otherwise.
        """
        if service not in self.available_services:
            raise typer.BadParameter(f"{service} is not a valid service. Valid service to run are {COMPONENTS}")
        return True

    
    def _check_if_images_exist(self, images: list) -> bool:
        """
        Check if the images exist. If they don't, pull them.

        Parameters
        ----------
        images: list
            List of images to check.
        
        Returns
        -------
        bool
            True if the images exist, raises an error otherwise.
        """
        for image in images:
            image_name = f"{image[0]}:{image[1]}"
            try:
                self.client.images.get(image_name)
                typer.echo(f"Image {image_name} already exists, skipping download.")
            except docker.errors.ImageNotFound:
                typer.echo(f"Image {image_name} not found, downloading.")
                self.client.images.pull(image[0], tag=image[1])
        return True

    
    def _check_if_container_exists(self, container_name: str) -> bool:
        """
        Check if the container exists.

        Parameters
        ----------
        container_name: str
            Name of the container to check.
        
        Returns
        -------
        bool
            True if the container exists, raises an error otherwise.
        """
        try:
            self.client.containers.get(container_name)
            return True
        except docker.errors.NotFound:
            return False


    def _run_interface(self) -> bool:
        """
        Run the interface. There is different steps to run the interface.
        - Check if the variables are set (they need to be different from the default `changeme`).
        - Check if the images exist. If they don't, pull them.
        - Check if the containers exist. If they do, skip the creation.
        - Run all the containers.

        Returns
        -------
        bool
            True if the interface components are running, raises an error otherwise.
        """
        typer.echo("Checking env variables...\n")
        config = env_variables(["pgadmin", "postgres", "api"])

        typer.echo("Pulling images needed for the interface\n")
        images = [("postgres", "13.4"), ("dpage/pgadmin4", "snapshot")]
        self._check_if_images_exist(images)

        data_dir = Path.cwd().joinpath("database")
        data_dir.joinpath("postgres-data").mkdir(exist_ok=True, mode=777)
        postgres_exist = self._check_if_container_exists("mkrich-postgres")
        if postgres_exist is True:
            typer.echo(f"Container mkrich-postgres already exists, skipping creation.")
        else:
            typer.echo("Building postgres database...")
            self.client.containers.run(
                "postgres", name="mkrich-postgres", restart_policy={"Name": "unless-stopped"},
                environment=config["postgres"], ports={5432: 5432}, detach=True,
                mounts=[
                    docker.types.Mount(
                        target="/docker-entrypoint-initdb.d/init.sql", 
                        source=str(data_dir.joinpath("init.sql")), 
                        type="bind"
                    ),
                    docker.types.Mount(
                        target="/var/lib/postgresql/data", 
                        source=str(data_dir.joinpath("postgres-data")),
                        type="bind"
                    )
                ]
            )

        pgadmin_exist = self._check_if_container_exists("mkrich-pgadmin")
        if pgadmin_exist is True:
            typer.echo(f"Container mkrich-pgadmin already exists, skipping creation.")
        else:
            typer.echo("Building pgadmin...")
            self.client.containers.run(
                "dpage/pgadmin4", name="mkrich-pgadmin", restart_policy={"Name": "unless-stopped"},
                environment=config, ports={5050: 80}, detach=True,
                volumes={"pgadmin-data": {"bind": "/var/lib/pgadmin", "mode": "rw"}},
            )

        interface_exist = self._check_if_container_exists("mkrich-interface")
        if interface_exist is True:
            typer.echo(f"Container mkrich-interface already exists, skipping creation.")
        else:
            typer.echo("Building interface...")
            dockerfile_path = str(Path.cwd().joinpath("interface"))
            self.client.images.build(tag="mkrich-interface:latest", path=dockerfile_path)
            self.client.containers.run(
                "mkrich-interface:latest", name="mkrich-interface", restart_policy={"Name": "unless-stopped"},
                environment=config, ports={8501: 8501}, detach=True,
            )

        return True

    def _run_serving(self) -> bool:
        """
        Run the serving. There is different steps to run the serving.
        - Check if the variables are set (they need to be different from the default `changeme`).
        - Check if the images exist. If they don't, pull them.
        - Check if the container exists. If it does, skip the creation.
        - Run the container.

        Returns
        -------
        bool
            True if the serving components are running, raises an error otherwise.
        """
        typer.echo("Checking env variables...\n")
        config = env_variables(["minio", "binance"])

        serving_exist = self._check_if_container_exists("mkrich-serving")
        if serving_exist is True:
            typer.echo(f"Container mkrich-serving already exists, skipping creation.")
        else:
            typer.echo("Building serving API...")
            dockerfile_path = str(Path.cwd().joinpath("api"))
            self.client.images.build(tag="mkrich-serving:latest", path=dockerfile_path)
            self.client.containers.run(
                "mkrich-serving:latest", name="mkrich-serving", restart_policy={"Name": "unless-stopped"},
                environment=config, ports={8081: 80}, detach=True,
            )

        return True


    def _run_training(self):
        """
        Run the training. There is different steps to run the training.
        - Check if the variables are set (they need to be different from the default `changeme`).
        - Change the Prefect backend server to the local one.
        - Pull all Prefect images and launch all the containers in detached mode.
        - Register the Prefect flows.

        Returns
        -------
        bool
            True if the training components are running, raises an error otherwise.
        """
        typer.echo("Checking env variables...\n")
        config = env_variables(["minio", "binance"])

        typer.echo("Pulling Prefect images needed for the training...\n")
        subprocess_cmd_to_str("prefect", "backend", "server")
        subprocess_cmd_to_str("prefect", "server", "start", "--detach")

        flows = Path.cwd().joinpath("training", "trainer_flow.py")
        flows_process = subprocess_cmd_to_str("python", str(flows))
        typer.echo(flows_process.returncode)

        return True


    def start_local_agent(self):
        """
        Start the local agent.
        """
        subprocess_cmd_to_str("prefect", "agent", "local", "start")
    

    def stop_training(self):
        """
        Stop all Prefect containers.
        """
        subprocess_cmd_to_str("prefect", "server", "stop")
        