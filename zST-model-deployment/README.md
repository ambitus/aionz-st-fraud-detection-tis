# AI on zLinux Model Deployment with Triton Inference Server (AI Toolkit)

We will deploy our fraud detection AI model using Triton Inference Server (TIS). We can utilize the AI Toolkit to leverage TIS for model deployment. This deployed AI model can then be integrated into applications within the zLinux environment.

## Prerequisites
- Must have Docker or Podman installed

## Build Triton Inference Server
Build docker image
```
docker build -t zst-tis .
```

## Integrate AI Model into Triton Inference Server
1. Add your model (.pmml file) to `ai-st-fraud-detection-tis/zST-model-deployment/zST/models` directory
2. Add your preprocessing .joblib file to ``ai-st-fraud-detection-tis/zST-model-deployment/zST/models`` directory

## Deploy Triton Inference Server
Run docker container
```
docker run --shm-size 1G -u root --rm -p8000:8000 -v//$PWD/zST/models:/models zst-tis tritonserver --model-repository=/models
```

## Run Sample Test
Run python script from terminal with ip/port of triton inference server
```
python test-inferencing/inference_request.py <ip:port>
```

## AI Model Deployment Complete!