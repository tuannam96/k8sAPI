from kubernetes import client, config
from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from typing import Optional
import yaml

namespace = 'default'
config.load_kube_config("k8s.conf")
core = client.CoreV1Api()
DEPLOYMENT_NAME = "nginx-deployment"

def create_pod(name_service, name_image, version, port: Optional[int] = 80):
    resp = None
    try:
        resp = core.read_namespaced_pod(name=name_service, namespace=namespace)
    except ApiException as e:
        if e.status !=404:
            print("Unknow error: {}".format(e))
            exit(1)
    if not resp:
        print(f"pod {name_service} does not exits. Creating it...")
        container = client.V1Container(image=f'{name_image}:{version}', name=f'{name_service}')
        pod_spec = client.V1PodSpec(containers=[container])
        pod = client.V1Pod(api_version='v1', kind='Pod', metadata={'name':f'{name_service}', 'labels': {'run': f'{name_service}'}}, spec=pod_spec)
        response = core.create_namespaced_pod(body=pod, namespace=namespace)
        manifest = {
            "kind": "Service",
            "apiVersion": "v1",
            "metadata": {
                "name": f'{name_service}'
            },
            "spec": {
                "selector": {
                    "run": f"{name_service}"
                },
                "type": "NodePort",
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 80,
                        "targetPort": 80
                    }
                ]
            }
        }
        
        try:
            api_response = core.create_namespaced_service(namespace, manifest, pretty='true')
            print(api_response)
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_endpoints: %s\n" % e)
        print("Done!")

def delete_pod(name_service):
    resp = None
    try:
        resp = core.read_namespaced_pod(name=name_service, namespace=namespace)
    except ApiException as e:
        if e.status !=404:
            print("Unknow error: {}".format(e))
            exit(1)
    if resp:
        print(f"project {name_service} is shuting down...")
        resp = core.delete_namespaced_pod(
            name=f'{name_service}',
            namespace='default',
            async_req=True
        )
        resp_svc = core.delete_namespaced_service(
            name=f'{name_service}',
            namespace='default',
            async_req=True
        )
        print ("Done!")

DEPLOYMENT_NAME = "nginx-deployment"


def create_deployment_object():
    # Configureate Pod template container
    container = client.V1Container(
        name="nginx",
        image="nginx:1.15.4",
        ports=[client.V1ContainerPort(container_port=80)],
        resources=client.V1ResourceRequirements(
            requests={"cpu": "100m", "memory": "200Mi"},
            limits={"cpu": "500m", "memory": "500Mi"}
        )
    )
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "nginx"}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    spec = client.V1DeploymentSpec(
        replicas=3,
        template=template,
        selector={'matchLabels': {'app': 'nginx'}})
    # Instantiate the deployment object
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=DEPLOYMENT_NAME),
        spec=spec)

    return deployment


def create_deployment(api_instance, deployment):
    # Create deployement
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace="default")
    print("Deployment created. status='%s'" % str(api_response.status))


def update_deployment(api_instance, deployment):
    # Update container image
    deployment.spec.template.spec.containers[0].image = "nginx:1.16.0"
    # Update the deployment
    api_response = api_instance.patch_namespaced_deployment(
        name=DEPLOYMENT_NAME,
        namespace="default",
        body=deployment)
    print("Deployment updated. status='%s'" % str(api_response.status))


def delete_deployment(api_instance):
    # Delete deployment
    api_response = api_instance.delete_namespaced_deployment(
        name=DEPLOYMENT_NAME,
        namespace="default",
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    print("Deployment deleted. status='%s'" % str(api_response.status))

apps_v1 = client.AppsV1Api()

deployment = create_deployment_object()

delete_deployment(apps_v1)

# create_deployment(apps_v1, deployment)





# create_pod("icomm", "nginx", "1.13", 80)

# delete_pod("icomm")

