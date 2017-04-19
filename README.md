# Playing Othello Using Deep Learning Neural Network

This is a final year project done by Argens Ng and his mentor Dr. K. P. Chan of the University of Hong Kong
------------------
For a compressed light weight version (just for playing)
- download Core.tar.gz
------------------
To play:
```
python Game.py
```
------------------
To train a neural network with existing data:	Set up network architecture
- set up input dimension and feature
- set up output dimension and feature
```
python Trainer.py
```
------------------
To test one or more neural networks:
- set up tags and networks in "doTests()"
- set up input feature (X2 is freemove and border and corner by default
```
python Tester.py
```
------------------
To generate training data:
```
python RawToStates.py
```
------------------
To decode data (if lost): setup output and input file
```
python decoder.py
```
------------------
To test tree expansion manually: comment out thread creation in Tree.init ()
```
python
```
```python
tree = Tree
tree.initialize ()
```
then use 

```python
tree.nextNode = tree.nextNode.expand ()
tree.currentNode.print()
tree.updateMove(x,y)
tree.currentNode.state.print()
tree.currentNode.children
tree.currentNode.value
```
accordingly