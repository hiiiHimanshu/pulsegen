"""
Quick verification script to check if the system is ready
"""
import sys
import os

def check_file_exists(filepath):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} {filepath}")
    return exists

def check_import(module_name):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✓ {module_name}")
        return True
    except ImportError as e:
        print(f"✗ {module_name} - {e}")
        return False

print("=" * 60)
print("SYSTEM READINESS CHECK")
print("=" * 60)

print("\n1. Checking required files...")
files_ok = True
files_ok &= check_file_exists("main.py")
files_ok &= check_file_exists("config.py")
files_ok &= check_file_exists("batch_processor.py")
files_ok &= check_file_exists("topic_extractor.py")
files_ok &= check_file_exists("review_fetcher.py")
files_ok &= check_file_exists("report_generator.py")
files_ok &= check_file_exists("requirements.txt")
files_ok &= check_file_exists("README.md")

print("\n2. Checking Python syntax...")
try:
    import py_compile
    py_compile.compile("main.py", doraise=True)
    py_compile.compile("config.py", doraise=True)
    print("✓ All Python files have valid syntax")
    syntax_ok = True
except py_compile.PyCompileError as e:
    print(f"✗ Syntax error: {e}")
    syntax_ok = False

print("\n3. Checking if dependencies are installed...")
print("   (Run 'pip install -r requirements.txt' if any are missing)")
deps_ok = True
deps_ok &= check_import("pandas")
deps_ok &= check_import("numpy")
deps_ok &= check_import("sentence_transformers")
deps_ok &= check_import("sklearn")
deps_ok &= check_import("google_play_scraper")

print("\n" + "=" * 60)
if files_ok and syntax_ok:
    print("✓ SYSTEM IS READY!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Generate sample data: python3 generate_sample_data.py --start-date 2024-06-01 --end-date 2024-06-30")
    print("3. Run the system: python3 main.py --app swiggy --date 2024-06-30")
    if not deps_ok:
        print("\n⚠ Some dependencies are missing. Install them first.")
else:
    print("✗ SYSTEM NOT READY - Please fix the issues above")
print("=" * 60)

