import subprocess
import os

if __name__ == "__main__":
    os.environ["INVOICE_SERVICE_HOST"] = "localhost"
    os.environ["RINGRING_SERVICE_HOST"] = "localhost"
    os.environ["TESTING_HOST"] = "docker.for.mac.host.internal"
    os.environ["PGHOST"] = "localhost"
    os.environ["PGPASSWORD"] = "mysecretpassword"

    subprocess.run("cd ../../service/ && docker-compose -f docker-compose.test.yml up  --build -d",
                   shell=True)

    subprocess.run("pytest -v --tb=short", shell=True)
