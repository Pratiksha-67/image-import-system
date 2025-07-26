import gdown, tempfile, os, hashlib

def iter_public_images(folder_id: str):
    """Yield metadata dicts for each image in a **public** Drive folder."""
    tmpdir = tempfile.mkdtemp()
    info = gdown.download_folder(id=folder_id, output=tmpdir, quiet=True, remaining_ok=True)
    for meta in info.get("files", []):
        if not meta.get("mimeType", "").startswith("image/"):
            continue
        local_path = os.path.join(tmpdir, meta["name"])
        yield {
            "id": meta["id"],
            "name": meta["name"],
            "size": os.path.getsize(local_path),
            "mime": meta["mimeType"],
            "path": local_path,
            "etag": hashlib.md5(open(local_path, "rb").read()).hexdigest(),
        }
