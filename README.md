Credit card fraud detection (without SWOP/SWCI)
=================================================

This example runs a Credit Card Fraud Detection algorithm [1] on the Swarm Learning platform, without using Swarm Operator (SWOP) or Swarm Command Interface (SWCI) nodes. It uses Keras and Tensorflow.

This example uses a subset of the data from [1] for each node. These subset datasets are biased with respect to the class and the volume of data.
This example uses two Swarm Learning (SL) nodes, each spawning its own Machine Learning (ML) node directly via `run-sl`, without the orchestration layer normally provided by SWOP and SWCI.

>  **_NOTE :_** Refer [Data license](/examples/fraud-detection/Data_license.md/) associated with this dataset.

The ML program is located in `workspace/fraud-detection/model/fraud-detection.py`.

This example shows the Swarm training of a Credit Card Fraud Detection model using two Machine Learning (ML) nodes. Unlike the standard example, Swarm Learning (SL) nodes are started directly with `run-sl`, and each SL node spawns and manages its own ML node using the `--ml-*` flags. This removes the need for SWOP and SWCI nodes entirely.

## Cluster Setup

The cluster setup for this example uses only one host, as shown in the figure below:
- host-1: 172.1.1.1

1. This example uses one Swarm Network (SN) node. The name of the docker container representing this node is **sn1**. sn1 is also the Sentinel Node. sn1 runs on host 172.1.1.1.
2. Two Swarm Learning (SL) nodes are started directly, each spawning its own Machine Learning (ML) node. The names of the docker containers representing these nodes are **sl1** and **sl2**, running ML containers **ml1** and **ml2** respectively. Both run on host 172.1.1.1.
3. Example assumes that License Server (APLS) already runs on host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.

## Running the Credit card fraud detection example

### 1. Clone Project Repository into Workspace
```bash
cd ~/swarm-learning/workspace/
git clone https://github.com/clearlynew/Fraud-Detection-Without-SWOP-SWCI.git fraud-detection
```

### 2. Generate Certificates
```bash
cd ~/swarm-learning/
cp -r examples/utils/gen-cert workspace/fraud-detection/
./workspace/fraud-detection/gen-cert -e fraud-detection -i 1
./workspace/fraud-detection/gen-cert -e fraud-detection -i 2
```

### 3. Delete certificates with "swop" and "swci" in their name
```bash
cd workspace/fraud-detection/cert
rm swop-* swci-*
cd ../../../
```

### 4. Create Docker Network (if not already created)
```bash
docker network create host-1-net
```

### 5. Create Separate Mount Directory
```bash
mkdir -p ~/swarm-learning/workspace/fraud-detection/tmp/sl1
mkdir -p ~/swarm-learning/workspace/fraud-detection/tmp/sl2
chmod -R 777 ~/swarm-learning/workspace/fraud-detection/tmp
```

### 6. Copy SwarmLearning Wheel and delete duplicate
```bash
cp ~/swarm-learning/lib/swarmlearning-*.whl \
~/swarm-learning/workspace/fraud-detection/ml-context/
rm workspace/fraud-detection/ml-context/swarmlearning-client-*.whl 2>/dev/null
```

### 7. Build ML Docker Image
```bash
docker build -t fraud-ml-env ~/swarm-learning/workspace/fraud-detection/ml-context
```

### 8. Run APLS (only if not running or not connected)
```bash
docker run -d \
--name apls \
--network host-1-net \
-v apls-volume:/hpe \
-p 5814:5814 \
--restart unless-stopped \
hub.myenterpriselicense.hpe.com/hpe_eval/autopass/apls:9.19
```

### Set Environment Variables (according to hostname -I)
```bash
export HOST_IP=172.1.1.1
export SN_IP=172.1.1.1
export APLS_IP=172.1.1.1
export SN_API_PORT=30304
```

### 9. Run SN (Swarm Network Node)
```bash
cd ~/swarm-learning
./scripts/bin/run-sn -d --name=sn1 \
--network=host-1-net \
--host-ip=${HOST_IP} \
--sentinel \
--sn-api-port=${SN_API_PORT} \
--key=workspace/fraud-detection/cert/sn-1-key.pem \
--cert=workspace/fraud-detection/cert/sn-1-cert.pem \
--capath=workspace/fraud-detection/cert/ca/capath \
--apls-ip=${APLS_IP}
```

### 10. Monitor SN until ready
```bash
docker logs -f sn1
```
Wait until you see:
```
swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304
```

### 11. Run SL1
```bash
./scripts/bin/run-sl -d --name=sl1 \
--network=host-1-net \
--host-ip=${HOST_IP} \
--sn-ip=${SN_IP} \
--sn-api-port=${SN_API_PORT} \
--sl-fs-port=16000 \
--key=workspace/fraud-detection/cert/sl-1-key.pem \
--cert=workspace/fraud-detection/cert/sl-1-cert.pem \
--capath=workspace/fraud-detection/cert/ca/capath \
--ml-image=fraud-ml-env \
--ml-name=ml1 \
--ml-entrypoint=python3 \
--ml-cmd=/tmp/test/model/fraud-detection.py \
-v ~/workspace/fraud-detection/tmp/sl1:/tmp/hpe-swarm \
--ml-v workspace/fraud-detection/model:/tmp/test/model \
--ml-v workspace/fraud-detection/data-and-scratch1/app-data:/app-data \
--ml-e DATA_DIR=/app-data \
--ml-e SCRATCH_DIR=/tmp/scratch \
--ml-e MIN_PEERS=2 \
--ml-e MAX_EPOCHS=16 \
--apls-ip=${APLS_IP}
```

### 12. Run SL2
```bash
./scripts/bin/run-sl -d --name=sl2 \
--network=host-1-net \
--host-ip=${HOST_IP} \
--sn-ip=${SN_IP} \
--sn-api-port=${SN_API_PORT} \
--sl-fs-port=17000 \
--key=workspace/fraud-detection/cert/sl-2-key.pem \
--cert=workspace/fraud-detection/cert/sl-2-cert.pem \
--capath=workspace/fraud-detection/cert/ca/capath \
--ml-image=fraud-ml-env \
--ml-name=ml2 \
--ml-entrypoint=python3 \
--ml-cmd=/tmp/test/model/fraud-detection.py \
-v ~/workspace/fraud-detection/tmp/sl2:/tmp/hpe-swarm \
--ml-v workspace/fraud-detection/model:/tmp/test/model \
--ml-v workspace/fraud-detection/data-and-scratch2/app-data:/app-data \
--ml-e DATA_DIR=/app-data \
--ml-e SCRATCH_DIR=/tmp/scratch \
--ml-e MIN_PEERS=2 \
--ml-e MAX_EPOCHS=3 \
--apls-ip=${APLS_IP}
```

### 13. Monitor Training
```bash
docker logs -f sl1
docker logs -f sl2
```

Swarm training will end with the following log message at the end:
`SwarmCallback : INFO : All peers and Swarm training rounds finished. Final Swarm model was loaded.`

Final Swarm model will be saved in each node's specific scratch directory, which is `workspace/fraud-detection/data-and-scratch<n>/app-data` directory.

### 14. Clean-up
To clean-up, force remove the container nodes of the previous run. If needed, take a backup of the container logs. Finally remove the docker network (`host-1-net`) and the `tmp` mount directories.
```bash
docker rm -f sl1 sl2 sn1 ml1 ml2
```

## References
1. M. L. G. - ULB, "Credit Card Fraud Detection," [Online]. Available: [https://www.kaggle.com/mlg-ulb/creditcardfraud](https://www.kaggle.com/mlg-ulb/creditcardfraud)
