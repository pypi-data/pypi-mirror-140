## Sentinel Laptop: Beta Version

"""MIT License

Copyright (c) 2021 Conservation X Labs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""



import argparse
import docker
import GPUtil
import json
import numpy as np
import os
import pandas as pd
from PIL import Image, ImageDraw
import requests
import tqdm
import time


## Define CLI Variables
parser = argparse.ArgumentParser()
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
parser.add_argument('--org', type=str,
                    help='which org to run')                
parser.add_argument('--model', type=str,
                    default=256, help='which model to run')
parser.add_argument('--version', type=str,
                    default='latest', help='version of model to run')                
opt = parser.parse_args()



def download(key,org):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']=key
    print(key)
    os.system("docker pull us-west2-docker.pkg.dev/sentinel-project-278421/{}/{}:latest".format(org,org))

def run(org,model,input_folder,output_folder='',img_size=256,thresh=40,visualize=False):
    # Convert Confidence Threshold to 0-1 from 0-100
    confidence_threshold = thresh/100
    client = docker.from_env()
    print(client.containers.list())
    # Download and start container if necessary
    if len(client.containers.list()) == 0:
        print('Creating Container (may take a while the first time)')
        container = client.containers.run("us-west2-docker.pkg.dev/sentinel-project-278421/{}/{}".format(org,org),detach=True, name=model,ports={8501:8501})
        time.sleep(10)
        print('Container created successfully')
    else:
        print('Container already exists')

    # Check resources available on current machine
    try:
        GPU_num = len(GPUtil.getAvailable())
        if GPU_num == 0:
            print('Starting tensorflow container optimized for CPUs')
        else:
            print('GPU support does not yet exist')
    except Exception as e:
        print('Error')
        GPU_num = 'Unknown'
    print(f"CPUs Available: {os.cpu_count()} GPUs Available: {GPU_num}")
    time.sleep(3)



    # Check the input folder exists (exit if it doesnt)
    if not os.path.exists(input_folder):
        exit('Input folder does not exist... Please Correct.')

    if output_folder == '':
        output_folder = os.path.join(input,"data")
    # Check if output folder exists, and create it if it doesn't
    if not os.path.exists(output_folder):
        print('Output folder does not exist... Creating.')
        os.makedirs(output_folder)

    ## Make list of files
    images = []
    for file in os.listdir(input_folder):
        if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
            images.append(os.path.join(input_folder, file))
    if len(images) == 0:
        exit('No images found')

    ## Loop through files
    pbar = tqdm.tqdm(total=len(images))
    k = 0


    # Initialize lists
    files       = []
    bboxes      = []
    class_ids   = []
    confidences = []

    while k < len(images):

        image = Image.open(images[k])
        image = image.resize([img_size,img_size])
        # Normalize and batchify the image
        im = np.expand_dims(np.array(image), 0).tolist()
        

        url = 'http://localhost:8501/v1/models/{}:predict'.format(model)
        data = json.dumps({"signature_name": "serving_default", "instances": im})
        headers = {"content-type": "application/json"}
        json_response = requests.post(url, data=data, headers=headers)
        try:
            predictions = json.loads(json_response.text)['predictions'][0]

            # Check there are any predictions
            if predictions['output_1'][0] > confidence_threshold:

                ## Continue to loop through predictions until the confidence is less than specified confidence threshold
                x = 0
                while True:
                    if predictions['output_1'][x]>confidence_threshold and x < len(predictions['output_1']):
                        files.append(images[k])
                        bboxes.append(predictions['output_0'][x])
                        class_ids.append(predictions['output_2'][x])
                        confidences.append(predictions['output_1'][x])

                        # Make pictures with bounded boxes if requested
                        if visualize:
                            # Draw bounding_box
                            draw = ImageDraw.Draw(image)
                            draw.rectangle([(bboxes[-1][1],bboxes[-1][0]),(bboxes[-1][3],bboxes[-1][2])],outline='red',width=3)

                            # Draw label and score
                            class_name = class_ids[-1]
                            result_text = str(class_name) + ' (' + str(confidences[-1]) + ')'
                            draw.text((bboxes[-1][1] + 10, bboxes[-1][0] + 10),result_text,fill='red')
                        
                        x = x + 1
                    else:
                        break
                
                # Make pictures with bounded boxes if requested
                if visualize:
                    image.save('{}/{}'.format(output_folder,os.path.basename(images[k])))
        except Exception as e:
            print(f'\n Error ({images[k]}): {e}')
        pbar.update(1)
        k = k + 1

    ## Make output csv
    print(f'\n Saving .csv of images')
    df = pd.DataFrame()
    df['file'] = files
    df['class_id'] = class_ids
    df['confidence'] = confidences
    df['bbox'] = bboxes
    df.to_csv(f'{opt.output}/_detections.csv')

    ## Clean up
    print('Shutting down container')
    container.stop()
    client.containers.prune()

if __name__ == "__main__":
    # download(r"C:\Users\Sam Laptop\Downloads\key.json",islandconservation)
    #run(opt.org,opt.model,opt.input,opt.output,opt.img_size,opt.thresh,visualize=opt.visualize)
    run()