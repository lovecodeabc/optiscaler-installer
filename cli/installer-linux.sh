#!/bin/bash

VERSION="0.0.1-alpha"
echo "Welcome to Optiscaler Installer version $(VERSION)! \n Optiscaler and Optiscaler Installer are free software and come with NO WARRANTY, unless
provided otherwise by law."
if [[$(uname -s) != "Linux"]]; then
    echo "You are not on Linux. Please use the Windows version of Optiscaler-Installer."
    exit 1
fi
