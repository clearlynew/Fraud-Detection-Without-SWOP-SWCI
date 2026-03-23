# 1. Clone Project Repository into Workspace

```bash
cd ~/swarm/swarm-learning/workspace/
git clone https://github.com/clearlynew/Fraud-Detection-Without-SWOP-SWCI.git fraud-detection
```

# 2. Generate Certificates

```bash
./workspace/fraud-detection/gen-cert -e fraud-detection -i 1
./workspace/fraud-detection/gen-cert -e fraud-detection -i 2
```

# 3. Delete certificates with "swop" and "swci" in their name

```bash
cd workspace/fraud-detection/cert
rm swop-* swci-*
```

# 4. Create Docker Network (if not already created)

```bash
docker network create host-1-net
```

# 5. Create Shared Mount Directory

```bash
mkdir -p /home/hima/swarm/swarm-learning/workspace/fraud-detection/tmp
chmod -R 777 /home/hima/swarm/swarm-learning/workspace/fraud-detection/tmp
```

# 6. Copy SwarmLearning Wheel

```bash
cp ~/swarm/swarm-learning/lib/swarmlearning-*.whl \
~/swarm/swarm-learning/workspace/fraud-detection/ml-context/
```

# 7. Build ML Docker Image

```bash
export DOCKER_API_VERSION=1.43
docker build -t fraud-ml-env ~/swarm/swarm-learning/workspace/fraud-detection/ml-context
```

# 8. Run APLS (only if not running or not connected)

```bash
docker run -d \
--name apls \
--network host-1-net \
-v apls-volume:/hpe \
-p 5814:5814 \
--restart unless-stopped \
hub.myenterpriselicense.hpe.com/hpe_eval/autopass/apls:9.19
```

# 9. Run SN (Swarm Network Node)

```bash
cd ~/swarm/swarm-learning

./scripts/bin/run-sn -d --name=sn1 \
--network=host-1-net \
--host-ip=sn1 \
--sentinel \
--sn-api-port=30304 \
--key=workspace/fraud-detection/cert/sn-1-key.pem \
--cert=workspace/fraud-detection/cert/sn-1-cert.pem \
--capath=workspace/fraud-detection/cert/ca/capath \
--apls-ip=apls
```

# 10. Monitor SN until ready

```bash
docker logs -f sn1
```

Wait until you see:

```
swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304
```

# 11. Run SL1

```bash
./scripts/bin/run-sl -d --name=sl1 --network=host-1-net --host-ip=sl1 --sn-ip=sn1 --sn-api-port=30304 --sl-fs-port=16000 \
--key=workspace/fraud-detection/cert/sl-1-key.pem \
--cert=workspace/fraud-detection/cert/sl-1-cert.pem \
--capath=workspace/fraud-detection/cert/ca/capath \
--ml-image=fraud-ml-env --ml-name=ml1 \
--ml-w=/tmp/test \
--ml-entrypoint=python3 \
--ml-cmd=model/fraud-detection.py \
-v /home/hima/swarm/swarm-learning/workspace/fraud-detection/tmp:/tmp/hpe-swarm \
--ml-v=/home/hima/swarm/swarm-learning/workspace/fraud-detection/tmp:/tmp/hpe-swarm \
--ml-v=workspace/fraud-detection/model:/tmp/test/model \
--ml-v=workspace/fraud-detection/data-and-scratch1/app-data:/platform/data \
--ml-v=workspace/fraud-detection/data-and-scratch1:/platform/scratch \
--ml-e DATA_DIR=/platform/data \
--ml-e SCRATCH_DIR=/platform/scratch \
--ml-e MIN_PEERS=2 \
--ml-e MAX_EPOCHS=3 \
--apls-ip=apls
```

# 12. Run SL2

```bash
./scripts/bin/run-sl -d --name=sl2 --network=host-1-net --host-ip=sl2 --sn-ip=sn1 --sn-api-port=30304 --sl-fs-port=17000 \
--key=workspace/fraud-detection/cert/sl-2-key.pem \
--cert=workspace/fraud-detection/cert/sl-2-cert.pem \
--capath=workspace/fraud-detection/cert/ca/capath \
--ml-image=fraud-ml-env --ml-name=ml2 \
--ml-w=/tmp/test \
--ml-entrypoint=python3 \
--ml-cmd=model/fraud-detection.py \
-v /home/hima/swarm/swarm-learning/workspace/fraud-detection/tmp:/tmp/hpe-swarm \
--ml-v=/home/hima/swarm/swarm-learning/workspace/fraud-detection/tmp:/tmp/hpe-swarm \
--ml-v=workspace/fraud-detection/model:/tmp/test/model \
--ml-v=workspace/fraud-detection/data-and-scratch2/app-data:/platform/data \
--ml-v=workspace/fraud-detection/data-and-scratch2:/platform/scratch \
--ml-e DATA_DIR=/platform/data \
--ml-e SCRATCH_DIR=/platform/scratch \
--ml-e MIN_PEERS=2 \
--ml-e MAX_EPOCHS=3 \
--apls-ip=apls
```

# 13. Monitor Training

```bash
docker logs -f ml1
docker logs -f ml2
```
