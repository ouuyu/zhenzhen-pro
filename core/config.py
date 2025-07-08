import httpx

BASE_URL = "http://172.28.1.17:3009/v1"
API_KEY = "sk-fLo3J9UUg2mgx54wxlQbnOluoxe4DQxqHTTHcqB2WL2fsK4h"
PROXY_URL = "https://ai-zhenzhen.yunzuoye.net"

ALLOWED_USERS = ['869006', '878865', '1058625', '1058626']

client = httpx.AsyncClient(timeout=httpx.Timeout(450))