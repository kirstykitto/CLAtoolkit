#!/usr/bin/env python
import os
import sys
import dotenv

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv.read_dotenv(os.path.join(BASE_DIR, ".env"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clatoolkit_project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
