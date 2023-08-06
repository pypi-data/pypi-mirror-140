import os
import tarfile
import zipfile


def zip_extract_to(zip_file, target_dir):
    with zipfile.ZipFile(zip_file) as z:
        z.extractall(target_dir)


def zip_extract(zip_file):
    target_dir, _ = os.path.splitext(zip_file)
    if os.path.isdir(target_dir):
        os.rmdir(target_dir)
    zip_extract_to(zip_file, target_dir)


def zip_create_to(target_dir, target, src_dir, *args):
    with zipfile.ZipFile(os.path.join(target_dir, target), 'w') as z:
        for file in args:
            z.write(os.path.join(src_dir, file), arcname=file)
        return target


def zip_create(target_dir, target, *args):
    zip_create_to(target_dir, target, target_dir, *args)


def tar_extract_to(tar_file, target_dir):
    with tarfile.TarFile(tar_file) as t:
        t.extractall(target_dir)


def tar_extract(tar_file):
    target_dir, _ = os.path.splitext(tar_file)
    if os.path.isdir(target_dir):
        os.rmdir(target_dir)
    tar_extract_to(tar_file, target_dir)


def tar_create_to(target_dir, target, src_dir, *args):
    with tarfile.open(os.path.join(target_dir, target), "w") as tar:
        for name in args:
            tar.add(os.path.join(src_dir, name), arcname=name)


def tar_create(target_dir, target, *args):
    tar_create_to(target_dir, target, target_dir, *args)
