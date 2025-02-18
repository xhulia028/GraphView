# Project Overview

This project contains a variety of simulation experiments organized into hierarchical directories. Below, you'll find an explanation of the structure, followed by the tree structure for reference.

## Data

The data can be found as a .zip file in the project's directory.

## Description

The project is divided into two main categories:

1. **`NormalExperiments`**: This directory contains simulations for different scenarios such as `fallingDrop`, `explodingLiquid`, and `constantVelocityCube`. 

2. **`PercentageExperiments`**: This directory focuses on experiments for percentage-based analyses. Similar to `experiments`, the organization follows a hierarchical structure under different scenarios.

3. **`CheckpointExperiments`**


Within these directories, the hierarchy provides specific details for each type of test, with subdirectories for variations and test types. The structure is repetitive,as indicated by the `...` in the tree structure.

## Tree Structure

Here is the detailed tree structure:

```
NormalExperiments
├── fallingDrop
│   ├── withTuning
│   │   ├── frequency_tests
│   │   │   ├── dynamicVlMerge
│   │   │   ├── fastParticleBuffer
│   │   ├── iteration_tests
│   │   │   ├── ...
│   ├── vlc_c08
│   │   ├── ...
│   ├── lc_c08
│   │   ├── ...
│   ├── vlc_c06
│   │   ├── ...
├── explodingLiquid
│   ├──..
├── constantVelocityCube
│   ├──..

percentageExperiments
├── fallingDrop
│   ├── vlc_c08
│   │   ├── frequency_tests
│   │   │   ├── dynamicVlMerge
│   │   │   ├── fastParticleBuffer0
│   │   │   ├── fastParticleBuffer01
│   │   │   ├── fastParticleBuffer001
│   │   │   ├── ...
│   │   ├── iteration_tests
│   │   │   ├── ...
│   ├── lc_c08
│   ├── vlc_c06
├── spinodalDecomposition
│   ├──...
```

# Running the Plotting Functions

There are several ways to generate the plots for your experiments. Follow the guidelines below to ensure proper execution:

## 1. Specify Values Manually

You can manually provide the required values for each plotting function by editing the corresponding scripts or calling the functions directly.

## 2. Run from the Experiment Directory

Navigate to the specific experiment directory using the terminal. For example:
```bash
cd /Experiments/fallingDrop/vlc_c08/frequency_tests
```


Run the plotting code from within this directory to use the appropriate data files.

## 3. Use the Main Functions

Each graph visualization file contains main functions you can execute. These functions are designed to simplify the process of generating plots.

---

## Important Notes

### Base Path Requirements

- If you specify a base path manually or change to a directory using `cd`, ensure the path ends with either `iteration_tests` or `frequency_tests`.
- If the path does not meet this requirement, the plotting functions will fail.

### Plotting Function Compatibility

- Functions like `ci_vs_rt_fp`, `buffer_vs_container`, and `compare_dvl_fp` are designed for data under `Experiments`. They will not work with data from `percentageExperiments`.
- `distribution_plots` is specifically for `percentageExperiments`. This function is compatible only with experiments containing the following folders:
  - `fastParticleBuffer0`
  - `fastParticleBuffer01`
  - `fastParticleBuffer001`
  - `fastParticleBuffer0001`
  - ...

---

## Questions or Issues

If you have any questions or encounter issues, feel free to contact me.


