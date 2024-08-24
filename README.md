# ImageEditApi

ImageEditApi is a web application that allows users to upload images, edit them using DALL·E, and store them in AWS S3. The application also uses PostgreSQL for managing image metadata. This project provides a robust solution for handling image uploads, transformations, and storage.


## Features

- **Image Upload:** Users can upload images which are then stored in an AWS S3 bucket.
- **Image Editing:** Uses DALL·E to generate edited versions of the uploaded images based on user prompts.
- **PostgreSQL Integration:** Stores image metadata and user information in a PostgreSQL database.

## Installation

### Prerequisites

 Python 3.8+
 Django 4.x
 Django REST Framework
 PostgreSQL
 AWS S3 bucket
 OpenAI API key

**Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/ImageEditApi.git
   cd ImageEditApi
```
   Install the required dependencies:
```sh
$ virtualenv venv
```
```sh
$ venv\scripts\activate


```
```sh
$ pip install -r requirements.txt


```
Configure Database Settings:

Update the DATABASES settings in server/core/settings.py to match your MySQL configuration:

```sh
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dbname',
        'USER': 'your_mysql_username',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
**Set Up Environment Variables:**

### Create a .env file in the project root and add the following:
```sh
OPENAI_API_KEY=your-openai-api-key
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=your-region


```
Apply database migrations:
```sh
$ python manage.py makemigrations


```
```sh
$ python manage.py migrate


```

Start the development server:
```sh
$ python manage.py runserver


```


## 1. User Authentication

### 1.1. Register

**Endpoint:** `/api/register/`  
**Method:** POST  
**Description:** Registers a new user.

**Request Body:**

```json
{
  "username": "bunny",
  "email": "bunny@gmail.com",
  "password": "password123"
}
```

**Response**
```json
{
    "password": "password123",
    "last_login": null,
    "email": "bunny@gmail.com",
    "username": "bunny"
}

```


### 1.2 Login

**Endpoint:** `/api/login/`  
**Method:** `POST`  
**Description:** Authenticates a user and returns tokens.

**Request Body:**
```json
{
  "username":"bunny",
  "email": "bunny@gmail.com",
  "password": "password123"
}

```

**Response**
```json
{
  "access_token": "<access_token>",
  "refresh_token": "<refresh_token>"
}
```
![image](https://github.com/user-attachments/assets/dc840b0d-a60e-44f2-bd1a-c5b3fba90047)



#
#

# 2 Image

### 2.1 Image upload and edit

#### Image for upload
![image](https://github.com/user-attachments/assets/43772a3d-2498-4f92-a9d9-653e38b76e4a)

 **URL:** `api/images/images/`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`

### Request Parameters

When sending a request to this endpoint, include the following form-data fields:

- **image** : The image file to be uploaded. It should be in PNG format.
- **prompt**: A text prompt for DALL·E to generate an edited version of the image.
Here’s an example of how to upload an image with an optional prompt using `curl`:

```bash
curl -X POST http://localhost:8000/images/ \
  -H "Authorization: Bearer your-auth-token" \
  -F "image=@/path/to/your/image.png" \
  -F "prompt=Describe what you want the image to look like"
```
![image](https://github.com/user-attachments/assets/5fc8278d-8884-4a86-a055-90307505adec)

### After Editing the image 
![image](https://github.com/user-attachments/assets/9f033f1f-c0d2-409f-8b8f-0a9eb248350f)



### 2.2 Image update

#### Image for update
![image](https://github.com/user-attachments/assets/43772a3d-2498-4f92-a9d9-653e38b76e4a)

 **URL:** `api/images/images/`
- **Method:** `PATCH`
- **Content-Type:** `multipart/form-data`

### Request Parameters

When sending a request to this endpoint, include the following form-data fields:

- **image** : The image file to be uploaded. It should be in PNG format.
- **prompt**: A text prompt for DALL·E to generate an edited version of the image.
Here’s an example of how to upload an image with an optional prompt using `curl`:

```bash
curl -X PATCH http://localhost:8000/images/ \
  -H "Authorization: Bearer your-auth-token" \
  -F "image=@/path/to/your/image.png" \
  -F "prompt=Describe what you want the image to look like"
```
![image](https://github.com/user-attachments/assets/74dba6a2-813a-492f-a413-7e2c20d54a3f)

### After Editing the image 
![image](https://github.com/user-attachments/assets/52d32bbe-ab76-43cf-acc8-7f5482a510d2)

### 2.3 Image Delete
#### Image Delete Endpoint

The image delete endpoint allows users to delete images from the system. It will remove the image from both the AWS S3 bucket and the database.

### Endpoint

- **URL:** `api/images/images/{id}/`
- **Method:** `DELETE`
- **Content-Type:** `application/json`

### Path Parameters

- **id** (required): The ID of the image to be deleted. This should be the unique identifier for the image in the database.

### Request Example

Here’s an example of how to delete an image using `curl`:

```bash
curl -X DELETE http://localhost:8000/images/1/ \
  -H "Authorization: Bearer your-auth-token"








