import argparse
import sys
import os
from src.kernel.workspace import WorkspaceManager

def main():
    parser = argparse.ArgumentParser(description="Aetheris Engineering Operating System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    parser_init = subparsers.add_parser("init", help="Initialize a new .aetheris workspace")
    parser_init.add_argument("--dir", default=os.getcwd(), help="Target directory")

    # cleanup command
    parser_cleanup = subparsers.add_parser("cleanup", help="Purge temporary cache and runtime files")
    subparsers.add_parser("purge", help="Alias for cleanup")

    # archive command
    parser_archive = subparsers.add_parser("archive", help="Compress the .aetheris workspace")
    parser_archive.add_argument("--out", default="aetheris_archive.zip", help="Output zip filename")

    # remove-project command
    parser_remove = subparsers.add_parser("remove-project", help="Delete the .aetheris workspace")
    parser_remove.add_argument("--force", action="store_true", help="Skip confirmation prompts")

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)

    project_dir = getattr(args, 'dir', os.getcwd())
    wm = WorkspaceManager(project_dir)

    if args.command == "init":
        wm.initialize_workspace()
    
    elif args.command in ["cleanup", "purge"]:
        wm.cleanup()
        
    elif args.command == "archive":
        wm.archive(output_filename=args.out)
        
    elif args.command == "remove-project":
        if not args.force:
            confirm = input("Are you sure you want to delete the .aetheris Engineering Brain? [y/N]: ")
            if confirm.lower() != 'y':
                print("Aborted.")
                sys.exit(0)
        wm.remove_project()

if __name__ == "__main__":
    main()
