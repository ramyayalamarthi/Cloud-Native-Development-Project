# Cloud-Native-Development 

This application allows users to upload image files and view their upload history. It integrates with Google Cloud Storage and uses the GEMINI API for automatic image description generation.

## Features
- **File Upload**: Users can upload image files (JPEG format). Each uploaded file is saved to the server and also uploaded to a Google Cloud Storage bucket.
- **Upload History**: Users can view a history of their previously uploaded files with clickable links to download them.
- **Image Description**: Automatically generates a short description of each image using the GEMINI API. The description is stored as a JSON file along with the image.

## Tech Stack
- **Backend**: Flask
- **Cloud Storage**: Google Cloud Storage for storing files
- **Frontend**: HTML5, CSS3, and Flask Jinja templating
- **Image Description**: GEMINI API for generating a description of uploaded images
