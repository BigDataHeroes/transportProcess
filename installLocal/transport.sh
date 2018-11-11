#!/bin/bash

source properties.sh

python3.7 transporte.py $inputMetro $inputEMT $ouPath $baseMadridG $baseBarriosG $ouPathAgg
