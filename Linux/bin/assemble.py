import os

# Configuration
SOURCE_DIRS = ['../up', '.']
TARGET_ROOT = './common/'
STRUCTURE_FILE = 'assemble.txt'  # Should contain your paths, one per line

def find_exact_source(path):
    """Look for the full path in all SOURCE_DIRS. Return full path if found, else None."""
    rel = os.path.relpath(path, TARGET_ROOT)
    # Prevent accidental deletion of root directories
    if rel in (".", "/", ""):
        return None
    for src in SOURCE_DIRS:
        candidate = os.path.join(src, rel)
        abscandidate = os.path.abspath(candidate)
        abs_common = os.path.abspath(TARGET_ROOT)
        if abscandidate == abs_common or abscandidate == os.path.abspath(src):
            continue
        if os.path.exists(candidate):
            return candidate
    return None

def find_all_files_by_name(filename):
    """Search for all files named 'filename' inside all SOURCE_DIRS, recursively."""
    found_files = []
    for src in SOURCE_DIRS:
        for root, dirs, files in os.walk(src):
            for file in files:
                if file == filename:
                    full_path = os.path.join(root, file)
                    abssrc = os.path.abspath(src)
                    abspath = os.path.abspath(full_path)
                    if abssrc == abspath:
                        continue # Don't ever delete the source dir itself
                    found_files.append(full_path)
    return found_files

def delete_path(path):
    """Safely delete a file or directory at the given path."""
    if not os.path.exists(path):
        print(f"Warning: Path does not exist, skipping: {path}")
        return
    abspath = os.path.abspath(path)
    if abspath in (os.path.abspath(TARGET_ROOT), os.path.abspath('.')):
        print(f"Warning: Attempted to delete critical directory: {abspath}. Skipping.")
        return
    if os.path.isdir(path):
        print(f"Deleting directory: {path}")
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)
    elif os.path.isfile(path):
        print(f"Deleting file: {path}")
        os.remove(path)
    else:
        print(f"Warning: {path} is not a file or directory. Skipping.")

def main():
    with open(STRUCTURE_FILE, 'r') as f:
        entries = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith('[')]

    # Keep a set so we don't delete files twice
    deleted = set()

    for entry in entries:
        norm_entry = entry.lstrip('./').strip()
        if not norm_entry or norm_entry in ('.', '/'):
            print(f"Warning: Invalid entry in assemble.txt: '{entry}'")
            continue

        # Check for the exact folder/file path
        full_target = os.path.join(TARGET_ROOT, norm_entry)
        src_path = find_exact_source(full_target)
        if src_path and src_path not in deleted:
            delete_path(src_path)
            deleted.add(os.path.abspath(src_path))
        else:
            print(f"Warning: Could not find source for: {full_target}")

        # Also check for files that match the basename, anywhere in source
        base_name = os.path.basename(norm_entry)
        if base_name:  # Only process if there's a basename
            for found_file in find_all_files_by_name(base_name):
                abs_found = os.path.abspath(found_file)
                if abs_found not in deleted:
                    delete_path(found_file)
                    deleted.add(abs_found)

if __name__ == '__main__':
    main()