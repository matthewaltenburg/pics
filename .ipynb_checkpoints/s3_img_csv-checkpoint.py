import boto3
import pathlib
import os
import json
import csv



def transfer_s3_files(bucket, dest_bucket):
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix='')
    with open('names.csv', 'w', newline='') as csvfile:
        fieldnames = ['filname', 'labels', 'confidence']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for page in pages:
            for obj in page['Contents']:
    #  key = paginator.paginate(Bucket=bucket, Prefix=' ')
    # for key in s3.list_objects(Bucket=bucket)['Contents']:
                file_extension =  pathlib.Path(obj['Key']).suffix
                if(file_extension == ".jpeg" or file_extension == ".png"):
                    print ("moving file " + obj['Key'])
                    #s3copy(obj['Key'], bucket, dest_bucket)
                    response = detect_labels(obj['Key'], bucket)
                    for label in response['Labels']:
                        writer.writerow({'filname': obj['Key'], 'labels': label['Name'], 'confidence': str(label['Confidence'])})
                     #   writer.writerow({'filname': obj['Key'], 'labels': 'name'})

def s3copy(key ,bucket, dest_bucket):
    s3 = boto3.resource('s3')
    copy_source = {
        'Bucket': bucket,
        'Key': key
    }
    s3.meta.client.copy(copy_source, dest_bucket, key)
    print("file copies "+ key)

def detect_labels(photo, bucket):

    client=boto3.client('rekognition')

    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=10)

    print('Detected labels for ' + photo) 
    print()   
    for label in response['Labels']:
        print ("Label: " + label['Name'])
        print ("Confidence: " + str(label['Confidence']))
        print ("Instances:")
        for instance in label['Instances']:
            print ("  Bounding box")
            print ("    Top: " + str(instance['BoundingBox']['Top']))
            print ("    Left: " + str(instance['BoundingBox']['Left']))
            print ("    Width: " +  str(instance['BoundingBox']['Width']))
            print ("    Height: " +  str(instance['BoundingBox']['Height']))
            print ("  Confidence: " + str(instance['Confidence']))
            print()

        print ("Parents:")
        for parent in label['Parents']:
            print ("   " + parent['Name'])
        print ("----------")
        print ()
    return response

def main():
    print ("reading data from S3, enter bucket name")
  #  source_bucketname = input()
    source_bucketname = "cemf-suan"
    print ("tranfering files to S3, enter destination bucket name")
    dest_bucketname = input()
    dest_bucketname = "sbbridledestbucket"
    transfer_s3_files(source_bucketname, dest_bucketname)



if __name__ == "__main__":
    main()