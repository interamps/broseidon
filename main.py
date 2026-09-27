import urllib.request

HEALTH_URL = "http://localhost:8080/health"


def wait_for_server(timeout=60):
    import time

    start = time.time()

    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=2) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(1)

    raise TimeoutError("llama server did not become ready")


def main():
    print("Waiting for llama server...")
    wait_for_server()

    print("llama server ready")

    from backend.api.allocator import allocate

    allocate()


if __name__ == "__main__":
    main()