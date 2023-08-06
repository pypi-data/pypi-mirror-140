<div align="center">

# catchment

An open-source Python package for catchment delineation 🔥<br>

</div>
<br>

<div align="center">

Figure Here

</div>
<br>


## ⚡&nbsp;&nbsp;Usage

### Install
```bash
pip install catchment
```
<br>


### Example
```python
import catchment

path = f'{catchment._path}/example.csv'
Q, date = catchment.load_streamflow(path)
b, KGEs = catchment.delineation(Q, date, area=276)
print(f'Best Method: {b.dtype.names[KGEs.argmax()]}')
```
<br>



## Project Structure
The directory structure of catchment looks like this:
```
├── methods                 <- implements for 12 catchment delineation methods
│
├── recession_analysis      <- tools for estimating recession coefficiency
│
├── param_estimate          <- backward and calibration approaches to estimate other parameters
│
├── comparison              <- an evaluation criterion to comparison different methods
│
├── requirements.txt        <- File for installing catchment dependencies
│
└── README.md
```
<br>

## 📌&nbsp;&nbsp;Todo


### Nolinear reservoir assumption
- Implement the nolinear reservoir assumption from the [paper](https://github.com/xiejx5/watershed_delineation/releases)
- Employ a time-varing recession coefficiency for catchment delineation
<br>

### Applicable to other time scales
1. The current version only applies to the daily scale
2. The package needs to be updated to support hourly catchment delineation
<br>

## 🚀&nbsp;&nbsp;Publications

### The following articles detail the 12 catchment delineation methods and their evaluation criterion.
- Xie, J., Liu, X., Wang, K., Yang, T., Liang, K., & Liu, C. (2020). Evaluation of typical methods for catchment delineation in the contiguous United States. Journal of Hydrology, 583, 124628. https://doi.org/10.1016/j.jhydrol.2020.124628
