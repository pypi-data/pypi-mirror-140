__version__ = "0.1.0"


from getpass import getpass
import json
from os import environ, path
from statistics import mode
import tarfile
from tempfile import TemporaryDirectory
from time import sleep
import requests

ECTOCET_API_ORIGIN = (
    "https://www.ectocet.com"
    if "ECTOCET_API_ORIGIN" not in environ
    else environ["ECTOCET_API_ORIGIN"]
)


def deploy(target, model):

    try:
        namespace, name, *rest = target.split("/")
        if len(rest) > 0:
            raise ValueError("Invalid target path: more than 2 segments")
    except:
        raise ValueError("Invalid target path: expected '<organization>/<model>'")

    deploy_key = getpass("Ectocet deploy key: ")

    with TemporaryDirectory() as tmp:

        print("Packing model", end="... ")
        model.save(path.join(tmp, "model", "1"))

        modelPath = path.join(tmp, "model.tar.gz")

        with tarfile.open(modelPath, "w:gz") as tar:
            tar.add(path.join(tmp, "model"))

        print("OK")
        print("Uploading model", end="... ")
        presigned_post_request = requests.post(
            ECTOCET_API_ORIGIN + "/api/trpc/deployments.withDeployKey.create",
            headers={"x-ectocet-deploy-key": deploy_key},
            json={
                "json": {
                    "namespace": namespace,
                    "name": name,
                    "framework": "TENSORFLOW",
                }
            },
        )
        if presigned_post_request.status_code >= 400:
            raise ValueError(
                "Invalid Ectocet deploy key (at least for model '{}'), you can find your key at {}/app/account".format(
                    target, ECTOCET_API_ORIGIN
                )
            )
        deployment = presigned_post_request.json()["result"]["data"]["json"]
        presigned_post = deployment["modelUpload"]

        with open(modelPath, "rb") as f:
            files = {"file": (modelPath, f)}
            http_response = requests.post(
                presigned_post["url"], data=presigned_post["fields"], files=files
            )

        if http_response.status_code >= 400:
            raise RuntimeError("Upload failed")

        print("OK")
        print("Deploying model", end="... ")

    while True:
        sleep(5)
        model_request = requests.get(
            ECTOCET_API_ORIGIN + "/api/trpc/deployments.withDeployKey.byId",
            headers={"x-ectocet-deploy-key": deploy_key},
            params={"input": json.dumps({"json": {"id": deployment["id"]}})},
        )
        if model_request.status_code >= 400:
            raise RuntimeError("Status check failed")

        model = model_request.json()["result"]["data"]["json"]

        if model["status"] == "ERRORED":
            raise RuntimeError("Deployemnt failed: " + model["errorMessage"])

        if model["status"] == "DEPLOYED":
            break

    print("OK")
    print("Your model is deployed and ready for predictions at:")
    for alias in model["aliases"]:
        print("- https://m.ectocet.com/{}/{}/{}".format(namespace, name, alias["name"]))
    print(
        "Manage this deployment's addresses (via its aliases) at {}/app/orgs/{}/m/{}".format(
            ECTOCET_API_ORIGIN, namespace, name
        )
    )
