# Getting started with python SDK for Flagship

This documents will describe how to implement the Flagship python SDK in few steps.

## Install the library

The python sdk is available on pip package manager. Simply type the following command in your terminal : 

`pip install flagship`

## Import Flagship in your project

First place the following import at the most apropriate location in your code : 

`from flagship import Flagship`

## Initialize Flagship

To initialize the library, get an instance of the Flagship class and call the inner start method passing a configuration :


`fs = Flagship()
fs.start(config(env_id))
`

## Create a visitor

`visitor = fs.createVisitor(id)`