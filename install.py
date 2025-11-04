#!/usr/bin/python3

import os
import argparse
import subprocess

def main():
    
    parser = argparse.ArgumentParser(description='Install Mythic infection payloads')
    parser.add_argument('--mythic-path', metavar='mythic path', type=str, nargs='?', help='Mythic path', dest='mythic_path')
    parser.add_argument('--uninstall', action='store_true', help='Uninstall', dest='uninstall')

    args = parser.parse_args()

    if not args.mythic_path:
        print("Please specify the mythic path with --mythic-path")
        exit(1)
   
    local_path = os.path.dirname(os.path.abspath(__file__))
    for dirname in  sorted(f for f in os.listdir(local_path) if os.path.isdir(os.path.join(local_path, f))):
        
        if dirname.endswith("Container"):
            if args.uninstall:

                for docker_name in os.listdir(os.path.join(local_path, dirname, "Payload_Type")):
                    if docker_name in ["__init__.py", ".keep"]:
                        continue
                
                    print("Uninstalling %s from mythic" % docker_name)
                    subprocess.run(["./mythic-cli", "uninstall", docker_name], cwd=args.mythic_path)
            else:
                print("Installing %s to mythic" % dirname)
                subprocess.run(["./mythic-cli", "install", "folder", os.path.join(local_path, dirname), "-f"], cwd=args.mythic_path)

if __name__=="__main__":
    main()
