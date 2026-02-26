#!/usr/bin/env python3
"""
CTGadgets - Complete E-commerce Website Installation Script
Modified to work in any directory
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class CTGadgetsInstaller:
    def __init__(self):
        # Create project in a dedicated folder
        self.base_dir = Path(__file__).parent / "CTGadgets_Website"
        self.base_dir.mkdir(exist_ok=True)
        
        # Change to project directory
        os.chdir(self.base_dir)
        
        self.project_name = "ctgadgets"
        self.python = sys.executable
        
        print(f"📁 Installing CTGadgets in: {self.base_dir}")
        
    def create_django_project(self):
        """Create Django project if it doesn't exist"""
        if not (self.base_dir / "manage.py").exists():
            print("🔧 Creating Django project...")
            # Create Django project
            subprocess.run([
                self.python, "-m", "django", "startproject", 
                self.project_name, "."
            ], check=True)
            
            # Create store app
            subprocess.run([
                self.python, "manage.py", "startapp", "store"
            ], check=True)
            
            print("✅ Django project created")
        else:
            print("✅ Django project already exists")
    
    def create_directory_structure(self):
        """Create all necessary directories"""
        dirs = [
            "store/templates/store",
            "store/templatetags",
            "static/css",
            "static/js",
            "static/images",
            "media/products",
            "media/categories",
        ]
        
        for dir_path in dirs:
            (self.base_dir / dir_path).mkdir(parents=True, exist_ok=True)
        
        print("✅ Directory structure created")
    
    def create_files(self):
        """Create all necessary Python and template files"""
        # This is where you'd copy all the file contents from my previous answer
        # For brevity, I'm showing the structure - you'll need to paste each file's content
        
        files_to_create = [
            ("store/models.py", "# Paste models.py content here"),
            ("store/views.py", "# Paste views.py content here"),
            ("store/admin.py", "# Paste admin.py content here"),
            ("store/urls.py", "# Paste urls.py content here"),
            ("store/context_processors.py", "# Paste context_processors.py content here"),
            ("store/forms.py", "# Paste forms.py content here"),
            ("store/templates/store/base.html", "<!-- Paste base.html content here -->"),
            ("store/templates/store/index.html", "<!-- Paste index.html content here -->"),
            ("static/css/style.css", "/* Paste style.css content here */"),
            ("static/js/main.js", "// Paste main.js content here"),
            ("requirements.txt", "Django==4.2.7\nPillow==10.1.0\ndjango-ckeditor==6.7.0\nstripe==7.5.0\npython-decouple==3.8\ndjango-crispy-forms==2.1\ncrispy-bootstrap5==0.7"),
        ]
        
        for file_path, content in files_to_create:
            full_path = self.base_dir / file_path
            if not full_path.exists():
                full_path.write_text(content)
                print(f"✅ Created: {file_path}")
    
    def install(self):
        """Run complete installation"""
        print("\n" + "="*60)
        print("  CTGadgets E-commerce Installation")
        print("="*60)
        
        # Create Django project first
        self.create_django_project()
        
        # Create directory structure
        self.create_directory_structure()
        
        # Create files
        self.create_files()
        
        print("\n✅ Installation structure created!")
        print(f"\n📁 Project location: {self.base_dir}")
        print("\nNext steps:")
        print("1. Copy the full code from my previous answer into each file")
        print("2. Run: pip install -r requirements.txt")
        print("3. Run: python manage.py migrate")
        print("4. Run: python manage.py createsuperuser")
        print("5. Run: python manage.py runserver")
        
        return True

def main():
    installer = CTGadgetsInstaller()
    installer.install()

if __name__ == "__main__":
    main()
