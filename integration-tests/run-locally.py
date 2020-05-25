import subprocess
import os
import sys

def start_dockerized_apps():
    if is_docker_container_running('postgres') and is_docker_container_running('ringring') and is_docker_container_running('invoices') and len(sys.argv) == 1:
        exit_code = subprocess.call(["./docker-run.sh", "--skip-build-step"])
    else:
        exit_code = subprocess.call("./docker-run.sh")

    if exit_code > 0:
        raise Exception('Starting dockerized app failed.')

def is_docker_container_running(container_name):
    return 'true' == subprocess.run("docker inspect -f '{{.State.Running}}' " + container_name, shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8").strip()

if __name__ == "__main__":
    os.environ["SERVICE_HOST"] = "localhost"
    os.environ["TESTING_HOST"] = "docker.for.mac.host.internal"
    os.environ["PGHOST"] = "localhost"
    os.environ["PGPASSWORD"] = "mysecretpassword"
    start_dockerized_apps()
    subprocess.call("pytest -v", shell=True)
