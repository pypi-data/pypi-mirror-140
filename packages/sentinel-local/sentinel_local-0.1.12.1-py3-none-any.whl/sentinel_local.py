## Sentinel Laptop: Beta Version
import argparse
from src import utils

    
def download():
    ## Define CLI Variables
    parser = argparse.ArgumentParser()
    parser.add_argument('--org', type=str,
                        help='which org to run')                     
    opt = parser.parse_args()
    utils.download(opt)

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true',
                    help='Download image') 
    parser.add_argument('--org', type=str,
                        help='which org to run')                
    parser.add_argument('--model', type=str,
                        default=256, help='which model to run')                      
    parser.add_argument('--input', type=str,
                        help='Folder to be processed')
    parser.add_argument('--output', type=str,
                        default='out',help='Folder to where results are put')                    
    parser.add_argument('--visualize', action='store_true',
                        help='Add bounded boxes to images')                 
    parser.add_argument('--thresh', type=int,
                        default=40, help='threshold of model')
    parser.add_argument('--img_size', type=int,
                        default=256, help='size of images into model')              
    opt = parser.parse_args()
    if opt.download:
        download()
    utils.run(opt)

if __name__ == '__main__':
    run()