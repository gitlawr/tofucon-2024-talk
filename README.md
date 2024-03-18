# tofucon-2024-talk

This repository is dedicated to the collection and analysis of public information from Terraform GitHub issues, comments and events. The data is collected from GitHub APIs and stored in a MongoDB database for further analysis.

## Prepare Data Set

You can collect the data in the following ways:

### Load from dump files

Run `mongorestore` to load data from dump files in the repository.

### Collect from scratch

1. Set the `GITHUB_TOKEN` environment. Unauth API calls can easily reach the GitHub API limit.
2. Run a mongodb locally, e.g., `docker run -v mongodbdata:/data/db -p 27017:27017 -d mongo`.

Run the `collector.py` to collect data from GitHub APIs.

## Run Analysis

Once the data set is ready, you can run each script to do analysis. The script file names should be descriptive.
