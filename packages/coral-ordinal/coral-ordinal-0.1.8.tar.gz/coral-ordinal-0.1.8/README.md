# Ordinal regression in Tensorflow Keras

[![PyPi version](https://badge.fury.io/py/coral-ordinal.svg)](https://pypi.org/project/coral-ordinal/)
[![PyPi downloads](https://img.shields.io/pypi/dm/coral-ordinal?style=flat)](https://pypi.org/project/coral-ordinal/)


Tensorflow Keras implementation of ordinal regression (aka ordinal classification) using consistent rank logits (CORAL) by Cao, Mirjalili, & Raschka (2019).

This package includes:

  * Ordinal output layer: `CoralOrdinal()`
  * Ordinal loss function: `OrdinalCrossEntropy()`
  * Ordinal error metric: `MeanAbsoluteErrorLabels()`
  * Ordinal activation function: `ordinal_softmax()`

This is a work in progress, so please post any issues to the [issue queue](https://github.com/ck37/coral-ordinal/issues). The package was developed as part of the Berkeley D-Lab's [hate speech measurement project](https://hatespeech.berkeley.edu) and paper (Kennedy et al. 2020).

**Acknowledgments**: Many thanks to [Sebastian Raschka](https://github.com/rasbt) for the help in porting from the [PyTorch source repository](https://github.com/Raschka-research-group/coral-cnn/).

Key pending items:

  * Function docstrings
  * Docs
  * Tests

## Installation

Install the stable version via pip:

```bash
pip install coral-ordinal
```

Install the most recent code on GitHub via pip:

```bash
pip install git+https://github.com/ck37/coral-ordinal/
```

## Dependencies

This package relies on Python 3.6+, Tensorflow 2.2+, and numpy.

## Example

This is a quick example to show a basic model implementation. With actual data one would also want to specify the input shape.

```python
import coral_ordinal as coral
NUM_CLASSES = 5
model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(32, activation = "relu"))
model.add(coral.CoralOrdinal(num_classes = NUM_CLASSES)) # Ordinal variable has 5 labels, 0 through 4.
model.compile(loss = coral.OrdinalCrossEntropy(),
              metrics = [coral.MeanAbsoluteErrorLabels()])
```

[See this colab notebook](https://colab.research.google.com/drive/1AQl4XeqRRhd7l30bmgLVObKt5RFPHttn) for extended examples of ordinal regression with MNIST (multilayer perceptron) and Amazon reviews (universal sentence encoder).

Note that the minimum value of the ordinal variable needs to be 0. If your labeled data ranges from 1 to 5, you will need to subtract 1 so that it is scaled to be 0 to 4.


## References

Cao, W., Mirjalili, V., & Raschka, S. (2019). [Rank-consistent ordinal regression for neural networks](https://arxiv.org/abs/1901.07884). arXiv preprint arXiv:1901.07884, 6. 

Kennedy, C. J., Bacon, G., Sahn, A., & von Vacano, C. (2020). [Constructing interval variables via faceted Rasch measurement and multitask deep learning: a hate speech application](https://arxiv.org/abs/2009.10277). arXiv preprint arXiv:2009.10277.
