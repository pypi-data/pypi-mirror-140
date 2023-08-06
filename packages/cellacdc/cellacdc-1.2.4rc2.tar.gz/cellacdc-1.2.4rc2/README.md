# <img src="https://github.com/SchmollerLab/Cell_ACDC/blob/main/cellacdc/resources/icons/assign-motherbud.svg" width="60" height="60"> Cell-ACDC

<img src="https://github.com/SchmollerLab/Cell_ACDC/blob/main/cellacdc/resources/figures/Fig1.jpg">

## What is Cell-ACDC?

### A Python framework with a user-friendly GUI for **segmentation**, **tracking** and **cell cycle annotations** of microscopy data

Feel free to **ask any question** in our [Discussions area](https://github.com/SchmollerLab/Cell_ACDC/discussions)!

You can check out our pre-print [here](https://www.biorxiv.org/content/10.1101/2021.09.28.462199v2) and Twitter thread [here](https://twitter.com/frank_pado/status/1443957038841794561?s=20).

Written in Python 3.8 by Francesco Padovani and Benedikt Mairhoermann.

Tested on Windows 10 (64 bit), macOS, and Linux Mint 20.1

*NOTE: This readme is not an exhaustive manual. Please find a **User Manual** (including detailed installation instructions) [here](https://github.com/SchmollerLab/Cell_ACDC/blob/main/UserManual/Cell-ACDC_User_Manual.pdf).*

## Overview

Let's face it, when dealing with segmentation of microscopy data we often do not have time to check that **everything is correct**, because it is a **tedious** and **very time consuming process**. Cell-ACDC comes to the rescue!
We combined the currently **best available neural network models** (such as [YeaZ](https://www.nature.com/articles/s41467-020-19557-4),
[Cellpose](https://www.nature.com/articles/s41592-020-01018-x), [StarDist](https://github.com/stardist/stardist), and [YeastMate](https://github.com/hoerlteam/YeastMate)) and we complemented them with a **fast and intuitive GUI**.

We developed and implemented several smart functionalities such as **real-time continuous tracking**, **automatic propagation** of error correction, and several tools to facilitate manual correction, from simple yet useful **brush** and **eraser** to more complex flood fill (magic wand) and Random Walker segmentation routines.

See below **how it compares** to other popular tools available (*Table 1 our our [pre-print](https://www.biorxiv.org/content/10.1101/2021.09.28.462199v2)*).

<p align="center">
  <img src="https://github.com/SchmollerLab/Cell_ACDC/blob/main/cellacdc/resources/figures/Table1.jpg" width="600">
</p>

## Is it only about segmentation?

Of course not! Cell-ACDC automatically computes **several single-cell numerical features** such as cell area and cell volume, plus the mean, max, median, sum and quantiles of any additional fluorescent channel. It even performs background correction, to compute the **protein amount and concentration**.

You can load and analyse single **2D images**, **3D data** (3D z-stacks or 2D images over time) and even **4D data** (3D z-stacks over time).

Finally, we provide Jupyter notebooks to **visualize** and interactively **explore** the data produced.

**Do not hesitate to contact me** here on GitHub (by opening an issue) or directly at my email francesco.padovani@helmholtz-muenchen.de for any problem and/or feedback on how to improve the user experience!

## Update v1.2.3

**NOTE: some users had issues installing the environment with this version. Please see this [issue](https://github.com/SchmollerLab/Cell_ACDC/issues/5) for a possible solution**

This release includes new segmentation models:
- Cellpose v0.8.0 with the models cyto2 and omnipose
- StarDist

## Update v1.2.2

This is the first release with **full macOS support**! Additionally, navigating through time-lapse microscopy data is now up to **10x faster** than previous versions.
More details [here](https://github.com/SchmollerLab/Cell_ACDC/releases/tag/v1.2.2)

## Installation using Anaconda (recommended)

*NOTE: If you don't know what Anaconda is or you are not familiar with it, we recommend reading the detailed installation instructions found in manual [here](https://github.com/SchmollerLab/Cell_ACDC/blob/main/UserManual/Cell-ACDC_User_Manual.pdf).*

1. Download the [latest release](https://github.com/SchmollerLab/Cell_ACDC/releases) of Cell-ACDC.
2. Install [Anaconda](https://www.anaconda.com/products/individual) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for **Python 3.8**
3. Unzip the Cell-ACDC source code, open a terminal and navigate with `cd` command to the Cell-ACDC folder
4. Update conda with `conda update conda`. Optionally, consider removing unused packages with the command `conda clean --all`
5. Install the environment with `conda env create --file environment.yml`. Creating the environment will take several minutes.

## Installation using Pip

1. Download the [latest release](https://github.com/SchmollerLab/Cell_ACDC/releases) of Cell-ACDC.
2. Download and install [Python 3.8](https://www.python.org/downloads/)
3. Unzip the Cell-ACDC source code, open a terminal and navigate with `cd` command to the Cell-ACDC folder
4. Upgrade pip with `pip install --updgrade pip`
5. Create a virtual environment with `python -m venv env`
6. Install all the dependencies with `pip install -r requirements.txt`

## Install from source

If you want to try out experimental features (and if you have time maybe report a bug or two :D), you can install the developer version from source as follows:

1. Clone the repo with the command `git clone https://github.com/SchmollerLab/Cell_ACDC.git`
2. Install [Anaconda](https://www.anaconda.com/products/individual) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for **Python 3.8**
3. Update conda with `conda update conda`. Optionally, consider removing unused packages with the command `conda clean --all`
5. Create a new conda environment with the command `conda create -n acdc python=3.8`
6. Install Cell-ACDC and all of the dependencies with the command `pip install -e ".[all]"`. Note that to run this command you need to navigate to the Cell-ACDC path that where you cloned it.

## Running Cell-ACDC (installed the latest version)

1. Open a terminal and navigate to Cell-ACDC folder
2. Activate the environment (conda: `conda activate acdc`, pip on Windows: `.\env\Scripts\activate`, pip on Unix: `source env/bin/activate`)
3. Navigate to `cellacdc` folder and run the main launcher with `python main.py`

## Running Cell-ACDC (installed from source)

1. Open a terminal and navigate to Cell-ACDC folder
2. Activate the environment (conda: `conda activate acdc`, pip on Windows: `.\env\Scripts\activate`, pip on Unix: `source env/bin/activate`)
3. Run the command `cellacdc` or just `acdc`

## Usage

For details about how to use Cell-ACDC please read the User Manual found in `Cell-ACDC/UserManual` folder.
