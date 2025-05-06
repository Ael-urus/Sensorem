'''
File: requirements_generator_ast.py

This script defines a class `RequirementsGenerator` that scans a Python project
using Abstract Syntax Trees (AST) to identify imported modules. It filters
built-in modules and attempts to find installed versions using `pip freeze`
to generate a `requirements.txt` file.

Author: aelurus
Description: Generate requirements.txt using AST parsing and environment lookup.
'''
import os
import sys
import subprocess
import ast
from typing import Set, Optional, Dict, List
import builtins


class RequirementsGenerator:
    """
    Generates a requirements.txt file for a Python project.

    It recursively scans Python files within a project directory, parses
    import statements using AST for robustness, filters out built-in and
    standard library modules, attempts to find versions of remaining modules
    from the current Python environment using 'pip freeze', and writes
    the results to a requirements.txt file with helpful comments.
    """
    def __init__(self, project_path: str = ".", output_filename: str = "requirements.txt"):
        """
        Initializes the RequirementsGenerator.

        Sets the project path to scan and the desired output filename.
        Initializes an empty set to store found module names and a set
        of known built-in/standard library module names for filtering.

        Args:
            project_path: The path to the project root directory to scan.
                          Defaults to the current directory (".").
            output_filename: The name of the file where dependencies will
                             be written. Defaults to "requirements.txt".
        """
        self.project_path = project_path
        self.output_filename = output_filename
        # Store unique module names found in code *before* filtering built-ins
        self._found_modules: Set[str] = set()

        # Initialize set of built-in/standard library modules for filtering
        self._builtin_modules: Set[str] = set(sys.builtin_module_names)
        # Add common standard library modules not strictly in sys.builtin_module_names (heuristic)
        self._builtin_modules.update({
            'collections', 'datetime', 'functools', 'itertools', 'math',
            'random', 're', 'json', 'logging', 'unittest', 'argparse',
            'warnings', 'abc', 'typing', 'io', 'queue', 'threading', 'time',
            'decimal', 'fractions', 'heapq', 'bisect', 'array', 'mmap',
            'os.path', # os.path is a module frequently imported directly
            'asyncio', 'concurrent', 'xml', 'html', 'csv', 'zipfile', 'tarfile',
            'configparser', 'socket', 'ssl', 'http', 'urllib', 'email', 'shutil',
            'tempfile', 'pathlib', 'dataclasses', 'enum', 'stat', 'fnmatch',
             'glob', 'linecache', 'locale', 'platform', 'pty', 'signal', 'textwrap',
             'traceback', 'types', 'uuid', 'weakref', 'webbrowser', 'zipapp', 'zipimport'
            # This list can be expanded based on common stdlib modules
        })


    def run(self) -> None:
        """
        Orchestrates the complete process of generating the requirements file.

        This is the main public method to call. It performs the following steps:
        1. Scans the project directory using AST to find all imported module names.
        2. Filters out built-in and standard library modules.
        3. Queries the current Python environment using 'pip freeze' to find
           installed versions of the remaining modules.
        4. Writes the filtered modules and found versions (if any) to the
           specified output file, including helpful comments.
        """
        self.scan_project() # Step 1: Find module names (using AST)
        # Step 2: Filtering happens before writing
        # Step 3: Getting versions happens during writing
        self.write_requirements_file(self.output_filename) # Step 4: Filter, Get versions, Write


    def scan_project(self) -> None:
        """
        Recursively walks through the project directory and processes Python files.

        Uses os.walk to traverse the directory tree and calls _process_file
        for each Python file found. Excludes common virtual environment and
        build directories.

        Modifies:
            self._found_modules: Adds names of potentially external modules
                                 found in import statements.
        """
        print(f"Starting AST scan in directory: {os.path.abspath(self.project_path)}")

        try:
            # Define directories to exclude from scanning
            dirs_to_exclude = set(['venv', '.venv', 'env', '.env', 'node_modules', '__pycache__', 'build', 'dist', '.git', '.pytest_cache', '.mypy_cache', '.tox', '.idea'])
            # Add exclusion for the output directory if it's within the project path
            # This prevents scanning the requirements.txt file if it already exists
            output_dir = os.path.dirname(self.output_filename)
            if output_dir and output_dir != '.' and os.path.exists(os.path.join(self.project_path, output_dir)):
                 dirs_to_exclude.add(output_dir)

            for racine, repertoires, fichiers in os.walk(self.project_path):
                # Modify the list of directories IN PLACE for os.walk to skip them
                repertoires[:] = [d for d in repertoires if d not in dirs_to_exclude]

                for fichier in fichiers:
                    if fichier.endswith(".py"):
                        filepath = os.path.join(racine, fichier)
                        # Skip the generator script itself to avoid listing its own imports
                        if os.path.abspath(filepath) == os.path.abspath(__file__):
                             # print(f"Skipping generator script: {filepath}") # Debugging
                             continue

                        # print(f"Processing file: {filepath}") # Optional for debugging
                        self._process_file(filepath) # Process the file using AST

            print(f"Finished AST scan. Found {len(self._found_modules)} potential unique module names (before filtering built-ins).")

        except Exception as e:
            print(f"An error occurred during directory scan: {e}", file=sys.stderr)


    def _process_file(self, filepath: str) -> None:
        """
        Reads a specific Python file, parses its AST, and extracts import names.

        This method is called by `scan_project` for each Python file found.
        It uses the `ast` module to reliably find `import` and `from ... import`
        statements while ignoring comments, strings, etc.

        Args:
            filepath: The full path to the Python file to process.

        Modifies:
            self._found_modules: Adds extracted top-level module names.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            IOError: If an error occurs while reading the file.
            SyntaxError: If the file contains invalid Python syntax that prevents AST parsing.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read() # Read the entire file content

            # --- AST Parsing ---
            try:
                tree = ast.parse(code) # Parse the code into an AST

                # Define a NodeVisitor to traverse the AST and find imports
                class ImportFinder(ast.NodeVisitor):
                    def __init__(self, modules_set: Set[str]):
                        self.modules_set = modules_set

                    # Visit nodes of type 'Import' (e.g., import os, import requests as req)
                    def visit_Import(self, node: ast.Import):
                        """Visits Import nodes and adds top-level module names."""
                        for alias in node.names:
                            # Get the top-level module name (e.g., 'os', 'requests', 'numpy.random' -> 'numpy')
                            top_level_module = alias.name.split('.')[0]
                            # Avoid adding empty strings or single dots from weird syntax,
                            # and ensure it's not a relative import starting with '.'
                            if top_level_module and top_level_module != '.' and not alias.name.startswith('.'):
                                # print(f"  AST Found Import: {top_level_module} from {alias.name}") # Debugging
                                self.modules_set.add(top_level_module)
                        self.generic_visit(node) # Continue traversing children nodes

                    # Visit nodes of type 'ImportFrom' (e.g., from package import module)
                    def visit_ImportFrom(self, node: ast.ImportFrom):
                        """Visits ImportFrom nodes and adds top-level package names."""
                         # Process only absolute imports (level == 0)
                        if node.level == 0 and node.module:
                            # Get the top-level module name (e.g., 'package.sub' -> 'package')
                            top_level_module = node.module.split('.')[0]
                             # Avoid adding empty strings or single dots
                            if top_level_module and top_level_module != '.':
                                # print(f"  AST Found ImportFrom: {top_level_module} from {node.module}") # Debugging
                                self.modules_set.add(top_level_module)
                        # Note: Relative imports (node.level > 0) are intentionally ignored
                        self.generic_visit(node) # Continue traversing children nodes

                # Instantiate the visitor and run it on the AST of the file
                finder = ImportFinder(self._found_modules)
                finder.visit(tree)

            except SyntaxError as e:
                print(f"Error parsing AST for file {filepath}: {e}", file=sys.stderr)
            except Exception as e:
                print(f"An unexpected error occurred during AST processing for file {filepath}: {e}", file=sys.stderr)

        except FileNotFoundError:
             print(f"Error: File not found {filepath}", file=sys.stderr)
        except IOError as e: # Catch other potential file reading errors
            print(f"Error reading file {filepath}: {e}", file=sys.stderr)


    def _get_installed_packages_with_versions(self) -> Dict[str, str]:
        """
        Executes 'pip freeze' in the current environment and parses the output.

        Returns:
            A dictionary where keys are package names (or potential import names
            after simple mapping) and values are their exact installed versions.
            Returns an empty dictionary if 'pip freeze' fails.

        Raises:
            FileNotFoundError: If the 'pip' command is not found.
            subprocess.CalledProcessError: If 'pip freeze' exits with an error status.
        """
        package_versions: Dict[str, str] = {}
        try:
            # Execute pip freeze command
            # capture_output=True catches stdout/stderr
            # text=True decodes stdout/stderr as text using default encoding
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'freeze'], # Use sys.executable -m pip for robustness
                capture_output=True,
                text=True,
                check=True # Raise CalledProcessError if command returns non-zero exit code
            )

            # Parse the output line by line (format: package==version)
            for line in result.stdout.splitlines():
                line = line.strip()
                if line and '==' in line:
                    # Split at the first '=='
                    parts = line.split('==', 1)
                    package_name = parts[0].strip()
                    version = parts[1].strip()
                    if package_name and version:
                        # Store package name -> version
                        package_versions[package_name] = version
                        # Simple mapping helper: store name with underscores if it has hyphens
                        if '-' in package_name:
                            package_versions[package_name.replace('-', '_')] = version
                        # Add common manual mappings (limited list)
                        if package_name == 'Pillow': package_versions['PIL'] = version
                        if package_name == 'scikit-learn': package_versions['sklearn'] = version
                        if package_name == 'beautifulsoup4': package_versions['bs4'] = version
                        # Add more known mappings here if encountered (e.g., python-dateutil -> dateutil)

        except FileNotFoundError:
            print("Error: 'pip' command not found. Make sure pip is installed and in your PATH.", file=sys.stderr)
            print("Cannot retrieve installed package versions.", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error running 'pip freeze': {e}", file=sys.stderr)
            print(f"Pip freeze stderr:\n{e.stderr}", file=sys.stderr)
            print("Cannot retrieve installed package versions.", file=sys.stderr)
        except Exception as e:
            print(f"An unexpected error occurred while getting installed packages: {e}", file=sys.stderr)
            print("Cannot retrieve installed package versions.", file=sys.stderr)


        # print(f"Debug: Installed packages map: {package_versions}") # Debugging
        return package_versions


    def write_requirements_file(self, output_filename: str) -> None:
        """
        Writes the found external dependencies with their versions to a file.

        Filters out built-in and standard library modules from the scanned
        imports. Attempts to find matching installed packages and their
        versions using data from `_get_installed_packages_with_versions`.
        Writes the results to the specified file, sorted alphabetically,
        using the '~=' version specifier, and includes helpful comments.

        Args:
            output_filename: The name of the file to write dependencies to.

        Raises:
            IOError: If an error occurs while writing to the output file.
        """
        # --- Step 1: Filter Built-in and standard library modules ---
        # Create a new set containing only modules NOT in our known built-ins/stdlib list
        external_modules = {
            module for module in self._found_modules if module not in self._builtin_modules
            # Optional/Complex: Add a check here if module name corresponds to a file/folder
            # within the project_path AND is NOT found in pip freeze. This helps filter
            # local project modules more accurately, but is non-trivial.
            # Example conceptual check (requires implementing _is_local_project_module):
            # if self._is_local_project_module(module):
            #    print(f"Skipping identified local module: {module}") # Debugging
            #    return False # Exclude if it's local
            # else:
            #    return True # Keep if it's not local or can't determine
        }

        if not external_modules:
            print("No external dependencies found by the scanner.")
            # Create an empty file or add a comment saying no deps found
            try:
                 with open(output_filename, 'w', encoding='utf-8') as f:
                     f.write("# No external dependencies found by the scanner in Python files.\n")
                     f.write("# This file was generated by requirements_generator_ast.py\n")
                 print(f"Created or updated requirements file '{output_filename}' indicating no dependencies found.")
            except IOError as e:
                print(f"Error writing empty file {output_filename}: {e}", file=sys.stderr)
            return


        # --- Step 2: Get installed packages and versions (already done in run, but called here) ---
        # Re-call or ensure data is available - _get_installed_packages_with_versions is called here
        # just before needing the data. It includes its own error handling.
        installed_packages = self._get_installed_packages_with_versions()


        try:
            # Sort the filtered set of external module names
            sorted_external_modules = sorted(list(external_modules))

            # Open the output file in write mode ('w') to overwrite existing content
            with open(output_filename, 'w', encoding='utf-8') as f:
                # --- Add comments at the top ---
                f.write("# This file lists project dependencies found by scanning source code.\n")
                f.write("# Generated using AST parsing and filtering built-in/standard library modules.\n")
                f.write(f"# Generated by {os.path.basename(__file__)}\n") # Dynamically include script name
                f.write("#\n")
                f.write("# To install these dependencies, it's highly recommended to use a virtual environment.\n")
                f.write("# With a virtual environment activated, run:\n")
                f.write(f"# pip install -r {output_filename}\n") # Include output filename in command example
                f.write("#\n")
                f.write("# Note:\n")
                f.write("# - Versions are based on 'pip freeze' from the environment where this script was run.\n")
                f.write("# - Modules not found in 'pip freeze' (potentially local project modules or complex package name mismatches)\n")
                f.write("#   are listed without versions.\n")
                f.write("# - Mapping of import names (e.g., 'sklearn') to package names (e.g., 'scikit-learn')\n")
                f.write("#   is attempted but may not be perfect for all packages.\n")
                f.write("#\n")
                f.write("# Dependencies:\n")
                f.write("#\n")

                # --- Write dependencies with versions ---
                written_count = 0
                for module_name in sorted_external_modules:
                    # Attempt to find the module name (or a mapped package name) in the installed packages dictionary
                    version = installed_packages.get(module_name) # Tries direct name and name with underscores if hyphens exist

                    if version:
                        # If version found, write with compatible release operator (~=)
                        # Use the exact version found by pip freeze for the ~= operator base
                        f.write(f"{module_name}~={version}\n")
                    else:
                        # If version not found (likely local project module, complex package name mismatch, or pip error), write name only
                        f.write(f"{module_name} # Version not found in pip freeze / potentially local or complex external dependency\n")

                    written_count += 1

            print(f"Successfully wrote {written_count} potential external dependencies to '{output_filename}'")

        except IOError as e:
            print(f"Error writing to output file {output_filename}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"An unexpected error occurred while writing dependencies: {e}", file=sys.stderr)


# --- How to use this class ---
if __name__ == "__main__":
    # Create an instance of the RequirementsGenerator class
    # Uses the current directory "." and default output file "requirements.txt"
    generator = RequirementsGenerator()

    # Run the complete process (scan, filter, get versions, write)
    generator.run()

    # --- Example usage notes ---
    # You can specify a different directory or output file:
    # generator = RequirementsGenerator(project_path='../my_other_project', output_filename='other_reqs.txt')
    # generator.run()

    # To generate documentation using pydoc, run from your terminal:
    # pydoc ./requirements_generator_ast.py
    # or (for HTML):
    # pydoc -w ./requirements_generator_ast.py