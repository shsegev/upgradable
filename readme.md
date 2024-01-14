# Upgradable Docker.

Sample docker that upgrades itself. and then restarts with the newer version.

## Usage
allflow.sh is the main script for testing the flow:
- Clear all relevant containers and images
- build the docker version 1.10
- tag it as latest (not really needed)
- Run the docker
- Build the docker version 1.11
- Save the image to a tar file
- Remove image 1.11
- view docker logs
- call docker update_new command
- update_new command will:
  - load the image from the tar file
  - tag it as latest
  - send sigterm
- onshutdown.sh will:
  - wait for 5 seconds
  - rename the old docker
  - set disable autorestart for old docker
  - start the new docker
  - NOT Implemented: at docker startup remove old docker
