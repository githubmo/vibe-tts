# NVIDIA Riva Setup Guide

## Prerequisites
- NVIDIA GPU (Volta or newer recommended)
- NVIDIA Driver (version 470.57.02 or later)
- Docker with NVIDIA Container Toolkit
- NGC Account (free): https://ngc.nvidia.com

## Quick Start

### 1. Install NVIDIA Container Toolkit
```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. Get NGC API Key
1. Sign up at https://ngc.nvidia.com
2. Go to Setup > API Key
3. Generate and save your API key

### 3. Download Riva Quick Start Scripts
```bash
# Login to NGC
docker login nvcr.io
# Username: $oauthtoken
# Password: <your-ngc-api-key>

# Download Riva Quick Start
ngc registry resource download-version nvidia/riva/riva_quickstart:2.16.0
cd riva_quickstart_v2.16.0
```

### 4. Configure Riva
Edit `config.sh`:
```bash
# Enable only TTS to save resources
service_enabled_asr=false
service_enabled_nlp=false
service_enabled_tts=true
service_enabled_nmt=false

# Use GPU 0
gpus_to_use="device=0"

# Optional: Change models
# For English male voice, the default models are fine
```

### 5. Initialize and Start Riva
```bash
# Initialize (downloads models - may take time)
sudo bash riva_init.sh

# Start Riva server
sudo bash riva_start.sh

# Check if running
docker ps | grep riva-speech
```

### 6. Test Connection
```bash
# Check server health
docker exec -it riva-speech riva_health
```

## Available Voices

Default English voices in Riva:
- `English-US-Male-1` - Male voice
- `English-US-Female-1` - Female voice

## Troubleshooting

### Port Already in Use
If port 50051 is taken:
1. Edit `config.sh`
2. Change `riva_speech_api_port="50051"` to another port
3. Update the app's server URL accordingly

### GPU Memory Issues
Reduce model size in `config.sh`:
```bash
# Use smaller models
models_tts="conformer_en_US_male_small"
```

### Check Logs
```bash
docker logs riva-speech
```

## Stop Riva
```bash
sudo bash riva_stop.sh
```

## Using Cloud/Remote Riva

If you have Riva running on a remote server:
1. Ensure port 50051 is accessible
2. In the TTS app, use: `your-server-ip:50051`

## Alternative: Riva on Cloud Providers

- **AWS**: Use NVIDIA GPU instances (g4dn, p3, p4)
- **Google Cloud**: Use NVIDIA T4/V100 instances
- **Azure**: Use NC-series VMs

For production, consider NVIDIA's hosted Riva services or deploy on Kubernetes.