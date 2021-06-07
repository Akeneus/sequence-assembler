# sequence-assembler

## Install
Install all base dependencies via "pip3 install .", if you want to export the graphs as raster graphics you have to install pycario. If pycario is not installed, do not try to export a plot directly, but use the generated graphviz file.

## Usage
The interactive program can be started with "python3 run.py" if you are in the root directory of this project. If you do not enter a value when prompted, No or a default value is assumed. The default values can be safely edited directly in the run.py.

**Parameters**

* Path: Path to the fragment file to be processed.
* MinWeight: minimum necessary overlap between two fragments to join them.
* BatchExecute: if yes, then several calculations are performed(DEFAULT=10) and the best one is returned. The result with the fewest fragments is assumed to be the best.
* PrintPlot: if yes, then raster graphics are created for each slice. use only if pycairo is installed.
* CoreAssembler: if yes, the file is processed with a simple assembler (task 1)
* DoubleHelixAssembler: if yes, the file will be processed with a DoubleHelixAssembler (Task 2)
* SubsitutionAssembler: if yes, the file will be processed with a SubsitutionAssembler (Task 3)

## Git branching model
The branching model of this Git is based on Vincent Driessen [proposal](https://nvie.com/posts/a-successful-git-branching-model/) from 2010

## Python style guide
As a reference style guide, the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) is used for this project

## Comments and Docstrings
As already proposed by [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) this project uses [docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)  to document the source-code