## Description

This database will hold everything about file according into the given access keys for the directory, this will be the main file server for all application

## Features

Basic file server requirement like, upload, perview, download, delete, move and copy files, supporting all type of documets properly.

All of those action need access keys that is correspond to which directory that is being accessable, currently we have MinIO directory like below:
- **employee/** - This is where all employee database document are resides
- **attendance/** - This is where attendance document are, like leave, sick, vacation documents that need to be in records
- **task/** - This is external support for task management files to be in

## Access Keys

Access keys are being split into 2 types, according to their usages, use them based on needed, on backend system you will have the full access key of read and write for your action, and on frontend you will be given read-only keys for preview and download

List of the access keys and their specification:
1. Read and write keys (size of hex 12byte)
2. Read-only keys (half turnecation of the read and write keys)

These keys are also being limited to where they can access on the MinIO directory, for example we currently have 3 full access keys for the directory listed on the features above, and 3 read-only keys for those directory as well
