import subprocess
import os
import run

def start_app():
    if is_docker_container_running('postgres') and is_docker_container_running('flask-ringring'):
        return

    if subprocess.call("./docker-run.sh") > 0:
        raise Exception('Starting dockerized app failed.')

def is_docker_container_running(container_name):
    return 'true' == subprocess.run("docker inspect -f '{{.State.Running}}' " + container_name, shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8").strip()


os.environ["SERVICE_HOST"] = "localhost"
start_app()
run.run_test_suite()
