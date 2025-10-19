#!/bin/bash
set -e

PACKAGE_DIR="package"
ZIP_FILE="deployment_package.zip"
PROJECT_ROOT=$(pwd)

echo "--- Cleaning up old package ---"
rm -rf ${PACKAGE_DIR} ${ZIP_FILE}

echo "--- Creating a fresh package directory ---"
mkdir -p ${PACKAGE_DIR}

echo "--- Creating a temporary virtual environment inside the package directory ---"
python3 -m venv ${PACKAGE_DIR}/venv

echo "--- Activating the temporary venv and installing production dependencies ---"
# the source command to activate the venv for the subsequent pip command
source ${PACKAGE_DIR}/venv/bin/activate
pip install -r ${PROJECT_ROOT}/requirements.txt

# Deactivate the temporary venv
deactivate

echo "--- Copying installed libraries to the root of the package directory ---"
# location for Lambda packages
SITE_PACKAGES_DIR="${PACKAGE_DIR}/venv/lib/python3.12/site-packages"
cp -r ${SITE_PACKAGES_DIR}/* ${PACKAGE_DIR}/

echo "--- Copying source code into package root ---"
cp ${PROJECT_ROOT}/src/*.py ${PACKAGE_DIR}/

echo "--- Cleaning up temporary venv files from package directory ---"
rm -rf ${PACKAGE_DIR}/venv
rm -rf ${PACKAGE_DIR}/bin
rm -rf ${PACKAGE_DIR}/lib
rm -rf ${PACKAGE_DIR}/include
rm -rf ${PACKAGE_DIR}/pyvenv.cfg

echo "--- Zipping deployment package ---"
cd ${PACKAGE_DIR}
zip -r ${PROJECT_ROOT}/${ZIP_FILE} .
cd ${PROJECT_ROOT}

echo "--- Cleaning up package directory ---"
rm -rf ${PACKAGE_DIR}

echo "--- Deployment package created successfully! ---"