import os


# Load environment variables (system variables) in the os.environ manager
def load_dotenv(env_path: str) -> None:
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, value = line.split('=', 1)
            os.environ[key] = value