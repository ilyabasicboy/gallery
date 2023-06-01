from pathlib import Path
from django.conf import settings


def create_symlink(path: str, file_name: str, title: str) -> None:

    symlink_dir = str(Path(settings.MEDIA_ROOT, settings.SYMLINKS_DIR, title))
    if not symlink_dir.exists():
        symlink_dir.mkdir(parents=True)
    src_path = str(Path(path))
    Path(symlink_dir, file_name).symlink_to(src_path)