import subprocess
import os


if __name__ == "__main__":
    os.environ["INVOICE_SERVICE_HOST"] = "localhost"
    os.environ["RINGRING_SERVICE_HOST"] = "localhost"
    os.environ["TESTING_HOST"] = "docker.for.mac.host.internal"
    os.environ["PGHOST"] = "localhost"
    os.environ["PGPASSWORD"] = "mysecretpassword"

    testing_dir = os.path.dirname(os.path.abspath(__file__))

    project_root = os.path.join(testing_dir, '..', '..')
    service_dir = os.path.join(project_root, 'service')

    subprocess.run(f"cd {service_dir} && docker-compose -f docker-compose.yml -f {testing_dir}/docker-compose.override.yml up --build -d", shell=True, check=True)
    subprocess.run(f"cd {project_root} && pytest -v --tb=short", shell=True)
    subprocess.run(f"cd {service_dir} && docker-compose down", shell=True, check=True)
