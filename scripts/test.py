DEFAULT_USER_ID = "chrome-extension-user"
from dotenv import load_dotenv
load_dotenv()

from mem0 import MemoryClient

mem0_client = MemoryClient()
memory = ' testing the word mummy'
mem0_client.add(memory, user_id=DEFAULT_USER_ID)
queries = ['amma', 'அம்மா', 'mother', 'mom']
for query in queries:
    results = mem0_client.search(query, user_id=DEFAULT_USER_ID)
    print('-'*100)
    print(f"Query: {query}")
    print(results)