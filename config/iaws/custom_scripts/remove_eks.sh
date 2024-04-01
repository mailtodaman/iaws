#!/bin/bash
echo "Removing EKS Cluster"
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sleep 2
/tmp/eksctl delete cluster --name my-cluster --region eu-west-2