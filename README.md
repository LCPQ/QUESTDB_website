# QUEST Website

## Introduction

The QUEST website has been designed to gather and analyze the highly-accurate vertical excitation energies produced by the [QUEST project](https://doi.org/10.1021/acs.jpclett.0c00014). 
The QUEST database contains more than 470 accurate vertical excitation energies of various natures ($\pi \to \pi^{*}$, $n \to \pi^{*}$, double excitation, Rydberg, singlet, doublet, triplet, etc) for small- and medium-sized molecules.
These values have been obtained using a combination of high-order coupled cluster and selected configuration interaction calculations using increasingly large diffuse basis sets.
One of the key aspect of the QUEST dataset is that it does not rely on any experimental values, avoiding potential biases inherently linked to experiments and facilitating in the process theoretical cross comparisons.
Following this composite protocol, we have been able to produce theoretical best estimates (TBEs) with the aug-cc-pVTZ basis set, as well as basis set corrected TBEs (i.e., near the complete basis set limit) for each of these transitions.
Thanks to the present website, one can easily test and compare the accuracy of a given method with respect to various variables such as the molecule size or its family, the nature of the excited states, the size of the basis set, etc.

## Quick start

To clone this website and use it locally please run the following commands.

```bash
git clone --recurse-submodules https://github.com/mveril/QUESTDB_website/
cd QUESTDB_website
hugo serve
```

Now you can use your favorite browser to navigate to the website using the URL showed by Hugo in your terminal (normally http://localhost:1313)

## Repository content

### The website

The main part of this repository is the website. It is built using the [hugo](https://gohugo.io/) static website generator with the [beautifulhugo](https://themes.gohugo.io/beautifulhugo/) theme.

All the data are stored in the [data](static/data) directory.

### The tools.

The second part is the [tools](tools/) a series of python and bash scripts used to generate data.

#### datafileBuilder

A python script to generate data from custom LaTeX input file see  [examples](docs/examples).

#### metarecover

The `metarecover` bash script is used to regenerate the metadata from the previous git history state.
So you can remove a data file to regenerate it from a LaTeX input file with `datafileBuilder` and recover the metadata from the previous version using `metarecover`.

### ADC25generator

The `ADC25generator` is used to build  `ADC(2.5)` data files from  `ADC(2)` and `ADC(3)` data files.

