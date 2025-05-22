# ⚡ Rate Limiter Code Challenge

This repository contains a configurable rate limiter using the Token Bucket algorithm.

This project includes:
- Dynamic rate limit updates via HTTP API
- CLI configuration via `argparse`
- Bash scripts for testing and interacting with the server


## 📦 Requirements
- Python 3.7+
- FastAPI
- Uvicorn
- `jq` (for readable curl output in Bash)
- `bc` (for handling fractions in shell)

# 🔩 Installation:
1. Install dependencies
```bash
sudo apt install jq bc 
pip install -r requirements.txt
```

# 🔧 Usage

1. First is necessary to run the server specifying the capacity (max requests) and refill rate of tokens (new tokens per second).
```bash
python run_server.py --capacity 10 --refill_rate 0.2
``` 
if no capacity and refill rate are specified, the program takes the default values (capacity=5  and refill_rate=0.5)

2. Then, open a new terminal and run the bash file to test the requests.
```bash
bash test_rate_limit.sh
``` 
This script asks first if the user wants to update the capacity and refill rate, if no it asks for number of requests to send to the server  via curl.

3. In case the user want to update the capacity and refill rate without running the file `test_rate_limit.sh`, is possible to do it in curl as follows:
```bash
curl -X POST http://localhost:8000/update \
     -H "Content-Type: application/json" \
     -d '{"capacity": 10, "refill_rate": 0.5}'
```  
After the updates, the user receives this message:
```bash
{"message":"Rate limit updated","new_config":{"capacity":10,"refill_rate":0.5}}
```