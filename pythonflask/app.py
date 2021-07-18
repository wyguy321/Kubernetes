from flask import Flask, request, jsonify
from kubernetes import client, config
from os import path
import os
import sys
import subprocess
import yaml
import json
app = Flask(__name__)

jcount = 1
premium = 1
def delete_job(api_instance):
    api_response = api_instance.delete_namespaced_job(
        name=JOB_NAME,
        namespace="default",
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    print("Job deleted. status='%s'" % str(api_response.status))

def create_job_object(job_name):
    # Configureate Pod template container
    container = client.V1Container(
        name="freeservice",
        image="mybuildimage",
        image_pull_policy="Never",
        command=["python3", "classify.py"])
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "pi"}),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]))
    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=4)
    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name),
        spec=spec)

    return job

def create_job(api_instance, job,nameSpace):
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace=nameSpace)
    print("Job created. status='%s'" % str(api_response.status))


@app.route('/img-classification/free', methods=['POST'])
#index_add_counter = 0

def free():
    global jcount
    content = request.get_json()
    seed = content["dataset"];
    print("SEED ",seed)
    filePath="jobprocess"+str(jcount)+".yaml"
    jcount+=1
    subprocess.call(['kubectl', 'apply', '-f', filePath])

    return '', 200
@app.route('/img-classification/premium', methods=['POST'])
#index_add_counter = 0
def premium_create():
    content = request.get_json()
    seed = content["dataset"];

    global premium
    content = request.get_json()
    seed = content["dataset"];
    print("SEED ",seed)
    filePath="jobprocesspremium"+str(premium)+".yaml"
    premium+=1
    subprocess.call(['kubectl', 'apply', '-f', filePath])
    #global seed
    #seed += 1
    #data = request.json
    #return jsonify(data)
    return '', 200
@app.route('/config', methods=['GET'])
#index_add_counter = 0
def kube_config():
    #content = request.get_json()
    #seed = content["dataset"];
    config.load_kube_config()
    v1 = client.CoreV1Api()
    ret = v1.list_pod_for_all_namespaces(watch=False)
    outerDictionary = {}
    #print("System PATH ",p)
    print("Listing pods with their IPs:")
    podsArray = []
    for i in ret.items:
        podsDictionary = {}
        podsDictionary["name"] = i.metadata.name;
        podsDictionary["ip"] = i.status.pod_ip;
        podsDictionary["namespace"] = i.metadata.namespace;
        podsDictionary["node"] = i.spec.node_name;
        podsDictionary["status"] = i.status.phase;
        podsArray.append(podsDictionary)

        print("###################################")
        print("ip:%s\tnamespace:%s\tname:%s\tstatus:%s NODENAME:%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name,i.status.phase, i.spec.node_name))
        print("###################################")
        #print(i)
    outerDictionary["pods"] = podsArray;
    #finalDict = json.dumps(outerDictionary)

    outeroutdict = {}

    outeroutdict["BODY"] = outerDictionary
    finalResult = json.dumps(outeroutdict)
    #print(finalDict)
    #global seed
    #seed += 1
    #data = request.json
    #return jsonify(data)
    return finalResult, 200
if __name__ == "__main__":
    app.run()
