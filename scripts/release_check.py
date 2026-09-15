from ml_stack.parity import ParityScanner
from ml_stack.adapters import generate

if __name__ == "__main__":
    report = ParityScanner(".").scan(); assert report["ok"], report["unclassified"]
    print(generate())
