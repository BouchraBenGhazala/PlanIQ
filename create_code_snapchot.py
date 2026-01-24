import os

def generate_code_snapshot(output_filename="code_snapshot.txt"):
    """
    Gathers only source code files from the project, excluding specified
    directories and file types, and combines them into a single text file.
    """
    # --- CONFIGURATION ---
    # 1. Add any folders you want to completely skip
    excluded_folders = {
        'venv', '.env', '__pycache__', '.git', '.vscode', 
        'demo', 'docs', 'data','checkpoints','docs(pour moi)','mlruns','screenshots'
    }

    # 2. Add specific files to skip
    excluded_files = {output_filename, '.gitignore','TSG_Cognitive Layer - T4.4 - Work Progress.pptx'}

    # 3. *** IMPORTANT: Only files with these extensions will be included ***
    #    Add any other source code extensions you use (e.g., '.js', '.css')
    allowed_extensions = {
        '.py', '.txt', '.md', '.json', '.html', '.css', '.js', 
        '.yaml', '.yml', '.toml', '.ini', 'Dockerfile', '.cfg'
        # Note: Add a dot for extensions. For files without extensions like 'Dockerfile', just list the name.
    }
    # --- END CONFIGURATION ---

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        print(f"Starting code snapshot... Output will be in '{output_filename}'")
        file_count = 0
        for root, dirs, files in os.walk('.', topdown=True):
            # Exclude specified directories from traversal
            dirs[:] = [d for d in dirs if d not in excluded_folders]

            for filename in files:
                # Check if the file should be skipped
                if filename in excluded_files:
                    continue

                # Check if the file extension is in our whitelist
                # This is the key change to prevent reading binary files.
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in allowed_extensions and filename not in allowed_extensions:
                    continue

                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
                        content = infile.read()
                        outfile.write(f"--- File: {filepath} ---\n")
                        outfile.write(content)
                        outfile.write("\n\n")
                        file_count += 1
                        print(f"  + Added: {filepath}")

                except Exception as e:
                    outfile.write(f"--- Error reading file {filepath}: {e} ---\n\n")

    print(f"\nSnapshot complete. Combined {file_count} files into '{output_filename}'.")

if __name__ == "__main__":
    generate_code_snapshot()