#!/bin/bash



function usage() {
    cat <<EOF
Usage: $0 IMAGE_NAME REGISTRY_PROJECT_ID TAG DEPLOY_YML [-n NAMESPACE] 
   
	IMAGE_NAME		the name of your image in the registry 
    	REGISTRY_PROJECT_ID	the google project name where the image is held 
    	TAG              	a version or commit tag (to identify in container registry)
        DEPLOY_YML       	path to deploy yml file (if default is not used)


    Optional:

	-n NAMESPACE        dev/prod tags for namespace (default: dev)

    Description:
	
	Custom variables (e.g. env variable for the container) but be provided in the 
	deploy.yml file. This script simply applies the deploy.yml file and deploys 
	the image from REGISTRY_PROJECT_NAME/IMAGE_NAME:TAG to the project that the
	developer is currently working under. In other words, using gcloud cli: 

	gcloud config set project your-fancy-project


    Example:

	$0 my-image my-registry-gcp-roject tag0.0.1 deploy.yml

	$0 usecase2 1e42bdbb5ffe7af83b
 
EOF
}

if  [ "$#" -lt "4" ]; then
	usage
	exit 1
fi

# handle args
IMAGE_NAME=$1
shift;
REGISTRY_PROJECT_ID=$1
shift;
TAG=$1
shift;
DEPLOY_YML=$1
shift;

# set defaults
NAMESPACE=dev

until [ -z "$1" ]; do
	case $1 in
        "-n") shift; NAMESPACE=$1;;
        *)
	esac
	shift
done


if kubectl delete pods $IMAGE_NAME --namespace $NAMESPACE &> /dev/null; then echo "deleted existing pod"; fi
sed -e "s/{{_IMAGE_NAME}}/$IMAGE_NAME/g" $DEPLOY_YML | 
	sed -e "s/{{_REGISTRY_PROJECT_ID}}/$REGISTRY_PROJECT_ID/g" | 
	sed "s/{{_NAMESPACE}}/$NAMESPACE/g"  | 
	sed "s/{{_TAG}}/$TAG/g" | 
	kubectl apply -f -


