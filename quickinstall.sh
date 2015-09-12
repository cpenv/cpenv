#!/bin/bash
sudo pip uninstall cpenv
sudo pip install .
rm -rf build
rm -rf cpenv.egg-info
rm -rf dist
