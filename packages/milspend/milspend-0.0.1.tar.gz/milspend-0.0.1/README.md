# defense
This is under review.

Using a SIPRI dataset, milspend can visualize military spending of up to four countries.

dataset is downloadable from:

https://sipri.org/sites/default/files/SIPRI-Milex-data-1949-2020_0.xlsx

<img src='https://github.com/ytakefuji/defense/blob/main/result.png' width=640 height=480>

# How to install milspend
You may need matplotlib library.

$ pip install matplotlib

$ pip install milspend

# How to run milspend

$ milspend USA China Russia Japan

<img src='https://github.com/ytakefuji/defense/raw/main/uscnrujp.png' height=480 width=640>

$ milspend Japan 'Korea, South'

<img src='https://github.com/ytakefuji/defense/raw/main/koreajapan.png' height=480 width=640>


# To run us_china_russia.py
SIPRI-Milex-data-1949-2020_0.xlsx file needs to be placed in the same directory as the following file us_china_russia.py.

$ python us_china_russia.py
