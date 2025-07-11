import subprocess

def install_requirements():
    subprocess.check_call(["pip", "install", "-r", "requirements.txt"])

if __name__ == "__main__":
    install_requirements()
    from utils.nltk_helper import ensure_nltk_resources
    ensure_nltk_resources()
