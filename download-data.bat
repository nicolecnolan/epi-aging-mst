curl --create-dirs http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz -o dataset/MNIST/raw/train-images-idx3-ubyte.gz
curl --create-dirs http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz -o dataset/MNIST/raw/train-labels-idx1-ubyte.gz
curl --create-dirs http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz -o dataset/MNIST/raw/t10k-images-idx3-ubyte.gz
curl --create-dirs http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz -o dataset/MNIST/raw/t10k-labels-idx1-ubyte.gz

py -m gzip -d dataset\MNIST\raw\train-images-idx3-ubyte.gz
py -m gzip -d dataset\MNIST\raw\train-labels-idx1-ubyte.gz
py -m gzip -d dataset\MNIST\raw\t10k-images-idx3-ubyte.gz
py -m gzip -d dataset\MNIST\raw\t10k-labels-idx1-ubyte.gz

