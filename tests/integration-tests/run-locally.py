import subprocess
import os


if __name__ == "__main__":
    os.environ["INVOICE_SERVICE_HOST"] = "localhost"
    os.environ["RINGRING_SERVICE_HOST"] = "localhost"
    os.environ["TESTING_HOST"] = "docker.for.mac.host.internal"
    os.environ["PGHOST"] = "localhost"
    os.environ["PGPASSWORD"] = "mysecretpassword"

    project_root = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), '..', '..')
    subprocess.run(
        f"cd {os.path.join(project_root, 'service')} && docker-compose -f docker-compose.test.yml up  --build -d", shell=True, check=True)
    subprocess.run(f"cd {project_root} && pytest -v --tb=short", shell=True)
