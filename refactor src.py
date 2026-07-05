import os
import re

def refactor_imports(target_directory):
    # --- Regex Patterns ---
    # 1. Patterns to remove 'src.'
    from_src_pattern = re.compile(r'^(\s*from\s+)src\.', re.MULTILINE)
    import_src_pattern = re.compile(r'^(\s*import\s+)src\.', re.MULTILINE)

    # 2. Patterns to swap 'logging' with 'diagnostics'
    # \b ensures we match the exact word 'logging' and not something like 'logging_utils'
    from_logging_pattern = re.compile(r'^(\s*from\s+)logging(\b)', re.MULTILINE)
    import_logging_pattern = re.compile(r'^(\s*import\s+)logging(\b)', re.MULTILINE)

    modified_count = 0

    # Walk through all directories and subdirectories
    for root, _, files in os.walk(target_directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Apply 'src.' removals
                    new_content = from_src_pattern.sub(r'\1', content)
                    new_content = import_src_pattern.sub(r'\1', new_content)
                    
                    # Apply 'logging' -> 'diagnostics' replacements
                    new_content = from_logging_pattern.sub(r'\1diagnostics\2', new_content)
                    new_content = import_logging_pattern.sub(r'\1diagnostics\2', new_content)
                    
                    # If changes were made, overwrite the file
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated: {file_path}")
                        modified_count += 1
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    print(f"\nRefactoring complete. Total files updated: {modified_count}")

if __name__ == "__main__":
    # Replace this with the path to the directory you want to search
    PROJECT_DIR = "." 
    
    # Safety check
    print("🛑 WARNING: This will permanently modify files in place.")
    print("Make sure you have backed up your code or committed it to Git first!")
    confirm = input(f"Proceed with refactoring '{PROJECT_DIR}'? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        refactor_imports(PROJECT_DIR)
    else:
        print("Operation cancelled.")