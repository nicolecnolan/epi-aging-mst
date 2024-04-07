curl --create-dirs http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz -o dataset/MNIST/raw/train-images-idx3-ubyte.gz
curl --create-dirs http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz -o dataset/MNIST/raw/train-labels-idx1-ubyte.gz
curl --create-dirs http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz -o dataset/MNIST/raw/t10k-images-idx3-ubyte.gz
curl --create-dirs http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz -o dataset/MNIST/raw/t10k-labels-idx1-ubyte.gz
cd dataset\MNIST\raw
wsl gunzip train-images-idx3-ubyte.gz
wsl gunzip train-labels-idx1-ubyte.gz
wsl gunzip t10k-images-idx3-ubyte.gz
wsl gunzip t10k-labels-idx1-ubyte.gz
