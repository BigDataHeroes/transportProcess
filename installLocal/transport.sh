#!/bin/bash

source activate keepcodingFinalProject
source properties.sh

python transporte.py $inputMetro $inputEMT $ouPath $baseMadridG $baseBarriosG $ouPathAgg
