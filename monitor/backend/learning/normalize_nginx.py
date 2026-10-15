def normalize_nginx(line, number):
    _, request_text, suffix = line.split('"', 2)
    method, path, _ = request_text.split()
    return {
        "id": f"nginx-{number}", "source": "nginx", "method": method,
        "path": path, "status_code": int(suffix.split()[0]), "raw": line,
    }
