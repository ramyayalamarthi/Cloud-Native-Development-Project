from google.cloud import storage

storage_client = storage.Client()

def get_list_of_files(bucket_name):
    blobs = storage_client.list_blobs(bucket_name)
    print(blobs)
    files = []
    for blob in blobs:
        files.append(blob.name)
    return files

def upload_file(bucket_name, file_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    return 

def download_file(bucket_name, file_name):
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(file_name)
    blob.download_to_filename(file_name)
    blob.reload()
    return
