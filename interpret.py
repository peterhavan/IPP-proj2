
import xml.etree.ElementTree as ET
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.parse_args()
    parser.add_argument("--source", help="source file")
    
if __name__ == '__main__':
    main()