[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Generic badge](https://img.shields.io/badge/Version-0.4.1-<COLOR>.svg)](https://shields.io/)
[![DOI](https://zenodo.org/badge/357129295.svg)](https://zenodo.org/badge/latestdoi/357129295)



# Grayscale to Color Semantic Mask Converotr

## Bug Fixes
Fixed `ValueError` raised while using Custom color pallet.

## Dependencies

```
numpy
cv2
tensorflow
python >= 3.6
```

## Installation

```
pip install gray2color
```

This `lib` converts the grayscale semantic masks obtained at the output a CNN and fills it with colors for example in case of 
`cityscape` dataset you have 30 channels at the output of CNN and after using `argmax` to create one channel semantic mask you
get the following output

![alt text](https://github.com/Mr-TalhaIlyas/Converting-Grayscale-Semantic-Masks-to-Color/raw/master/screens/gray.png?raw=true)
which you can use for measuring `IOU`, `Dice` or other evaluation metrics. But it is a bit difficult for human visualization so this package 
converts the above output to following ouptut easy to visualize.
![alt text](https://github.com/Mr-TalhaIlyas/Converting-Grayscale-Semantic-Masks-to-Color/raw/master/screens/rgb.png)
## Usage

```python
import cv2
from gray2color import gray2color

mask = cv2.imread('../gray.png', 0)
rgb = gray2rgb(mask, use_pallet='cityscape', custom_pallet=None)

```

## Returns

A `uint8` image with values ranging from [0, 255] you can save via

```python
import cv2

rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)  #   becaues cv2 will change color channels before writing
cv2.imwrite('../rgb.png', rgb)
```
## Available Pallets
Available Pallets are `ade20k`, `cityscape`, `lip`, `pannuke`, `pascal`, `vistas` 
for details on all above pallets and their corresponding names visit [here](https://github.com/Mr-TalhaIlyas/Color-Pallets-and-Class-Names-for-Semantic-Segmentation-Datasets)


## Usage with custom pallets
You can also define your custom color Pallets as follows

```python

# values are in order [R, G, B] ranging from [0, 255]

c_pallet = np.array([[[128, 64, 128],
                    [244, 35, 232],
                    [70, 70, 70],
                    [102, 102, 156],
                    [190, 153, 153]]], np.uint8) / 255
```
```python

rgb = gray2rgb(mask, use_pallet=None, custom_pallet=c_pallet)
```

## Raises Errors

```python

PalletNotDefined: if pallet is not specified

NotEnoughColors: if grayscale mask has more classes present than the colors in the pallet

```


For more details visit [GitHub](https://github.com/Mr-TalhaIlyas/Converting-Grayscale-Semantic-Masks-to-Color)