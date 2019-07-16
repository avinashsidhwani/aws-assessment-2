# Scalable Architecture:
# 
# Create a Lambda function. It's code is mentioned below.
# attach an S3 trigger to it. set it up by selecting the source-bucket and Event type as "All object create events"
# 



import boto3
import PIL
from PIL import Image
from io import BytesIO
from os import path

s3 = boto3.resource('s3')
src_b = 'av-a2-q2'
dest_b = 'av-a2-q2-r'
size = 200

def lambda_handler(event, context):
    for key in event.get('Records'):
        obj_key = key['s3']['object']['key']
        extension = path.splitext(obj_key)[1].lower()

        # getting the source file
        obj = s3.Object(
            bucket_name=src_b,
            key=obj_key,
        )
        obj_body = obj.get()['Body'].read()
    
        # resizing the image
        if extension in ['.jpeg', '.jpg']:
            format = 'JPEG'
        if extension in ['.png']:
            format = 'PNG'
        img = Image.open(BytesIO(obj_body))
        
        w, h = img.size[0], img.size[1]
        if w >= h:
            if w < size:
                wsize = w
                hsize = h
            else:
                wsize = size
                wratio = (wsize / float(w))
                hsize = int((float(h) * float(wratio)))
        else:
            if h < size:
                wsize = w
                hsize = h
            else:
                hsize = size
                hratio = (hsize / float(h))
                wsize = int((float(w) * float(hratio)))
        
        img = img.resize((wsize, hsize), PIL.Image.ANTIALIAS)
        buffer = BytesIO()
        img.save(buffer, format)
        buffer.seek(0)

        # Uploading the image
        obj = s3.Object(
            bucket_name=dest_b,
            key="resized_" + str(obj_key),
        )
        obj.put(Body=buffer)
