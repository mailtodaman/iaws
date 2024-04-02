#!/bin/bash
echo "Create EKS Cluster"
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sleep 2
/tmp/eksctl create cluster --name my-cluster --region eu-west-2 --node-type t3.small --nodes 3 --nodes-min 1 --nodes-max 3 --managed