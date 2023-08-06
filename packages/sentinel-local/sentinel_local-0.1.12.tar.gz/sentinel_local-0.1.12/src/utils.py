import os
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
import sys

def run(opt):
    # Convert Confidence Threshold to 0-1 from 0-100
    confidence_threshold = opt.thresh/100
    client = docker.from_env()
    
    if len(client.containers.list(filters={'ancestor':"us-west2-docker.pkg.dev/sentinel-project-278421/{}/{}".format(opt.org,opt.org)})) == 0:
        # Download and start container if necessary
        container = client.containers.run("us-west2-docker.pkg.dev/sentinel-project-278421/{}/{}".format(opt.org,opt.org),detach=True, name=opt.model,ports={8501:8501})
        time.sleep(10)
        print('Container created successfully')
    else:
        print('Container was already active')

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
    if not os.path.exists(opt.input):
        exit('Input folder does not exist... Please Correct.')

    if opt.output == '':
        opt.output = os.path.join(opt.input,"data")
    # Check if output folder exists, and create it if it doesn't
    if not os.path.exists(opt.output):
        print('Output folder does not exist... Creating.')
        os.makedirs(opt.output)

    ## Make list of files
    images = []
    for file in os.listdir(opt.input):
        if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
            images.append(os.path.join(opt.input, file))
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
        image = image.resize([opt.img_size,opt.img_size])
        # Normalize and batchify the image
        im = np.expand_dims(np.array(image), 0).tolist()
        

        url = 'http://localhost:8501/v1/models/{}:predict'.format(opt.model)
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
                        if opt.visualize:
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
                if opt.visualize:
                    image.save('{}/{}'.format(opt.output,os.path.basename(images[k])))
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

def download(opt):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']='key.json'
    os.system("docker pull us-west2-docker.pkg.dev/sentinel-project-278421/{}/{}:latest".format(opt.org,opt.org))