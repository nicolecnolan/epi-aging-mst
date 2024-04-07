# -*- coding: utf-8 -*-
"""autoencoder_good.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kM0qy3iYxexXa87gngoNKLA_IVA5rq1a
"""

import matplotlib.pyplot as plt # plotting library
import numpy as np # this module is useful to work with numerical arrays
import pandas as pd
import random
import torch
import torchvision
from torchvision import transforms
from torch.utils.data import DataLoader,random_split
from torch import nn
import torch.nn.functional as F
import torch.optim as optim

data_dir = 'dataset'

train_dataset = torchvision.datasets.MNIST(data_dir, train=True, download=True)
test_dataset  = torchvision.datasets.MNIST(data_dir, train=False, download=True)

train_transform = transforms.Compose([
transforms.ToTensor(),
])

test_transform = transforms.Compose([
transforms.ToTensor(),
])

train_dataset.transform = train_transform
test_dataset.transform = test_transform

m=len(train_dataset)

train_data, val_data = random_split(train_dataset, [int(m-m*0.2), int(m*0.2)])
batch_size=256

train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size)
valid_loader = torch.utils.data.DataLoader(val_data, batch_size=batch_size)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size,shuffle=True)

class Encoder(nn.Module):
    def __init__(self, encoded_space_dim,fc2_input_dim):
        super().__init__()

        self.encoder_cnn = nn.Sequential(
            nn.Conv2d(1, 8, 3, stride=2, padding=1),
            nn.ReLU(True),
            nn.Conv2d(8, 16, 3, stride=2, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(True),
            nn.Conv2d(16, 32, 3, stride=2, padding=0),
            nn.ReLU(True)
        )

        self.flatten = nn.Flatten(start_dim=1)

        self.encoder_lin = nn.Sequential(
            nn.Linear(3 * 3 * 32, 128),
            nn.ReLU(True),
            nn.Linear(128, encoded_space_dim)
        )

    def forward(self, x):
        x = self.encoder_cnn(x)
        x = self.flatten(x)
        x = self.encoder_lin(x)
        return x


class Decoder(nn.Module):
    def __init__(self, encoded_space_dim,fc2_input_dim):
        super().__init__()
        self.decoder_lin = nn.Sequential(
            nn.Linear(encoded_space_dim, 128),
            nn.ReLU(True),
            nn.Linear(128, 3 * 3 * 32),
            nn.ReLU(True)
        )

        self.unflatten = nn.Unflatten(dim=1,
        unflattened_size=(32, 3, 3))

        self.decoder_conv = nn.Sequential(
            nn.ConvTranspose2d(32, 16, 3,
            stride=2, output_padding=0),
            nn.BatchNorm2d(16),
            nn.ReLU(True),
            nn.ConvTranspose2d(16, 8, 3, stride=2,
            padding=1, output_padding=1),
            nn.BatchNorm2d(8),
            nn.ReLU(True),
            nn.ConvTranspose2d(8, 1, 3, stride=2,
            padding=1, output_padding=1)
        )

    def forward(self, x):
        x = self.decoder_lin(x)
        x = self.unflatten(x)
        x = self.decoder_conv(x)
        x = torch.sigmoid(x)
        return x

def train_epoch(encoder, decoder, device, dataloader, loss_fn, optimizer):
    # Set train mode for both the encoder and the decoder
    encoder.train()
    decoder.train()
    train_loss = []
    for image_batch, _ in dataloader:
        # Move tensor to device first
        image_batch = image_batch.to(device)
        # Encode data
        encoded_data = encoder(image_batch)
        # Decode data
        decoded_data = decoder(encoded_data)
        # Evaluate loss
        loss = loss_fn(decoded_data, image_batch)
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        # Print batch loss
        #print('\t partial train loss (single batch): %f' % (loss.data))
        train_loss.append(loss.detach().cpu().numpy())

    return np.mean(train_loss)

def test_epoch(encoder, decoder, device, dataloader, loss_fn):
    # Set evaluation mode
    encoder.eval()
    decoder.eval()
    with torch.no_grad():
        # Define the lists to store the outputs for each batch
        conc_out = []
        conc_label = []
        for image_batch, _ in dataloader:
            # Move tensor to the proper device
            image_batch = image_batch.to(device)
            # Encode data
            encoded_data = encoder(image_batch)
            # Decode data
            decoded_data = decoder(encoded_data)
            # Append the network output and the original image to the lists
            conc_out.append(decoded_data.cpu())
            conc_label.append(image_batch.cpu())
        # Create a single tensor with all the values in the lists
        conc_out = torch.cat(conc_out)
        conc_label = torch.cat(conc_label)

        val_loss = loss_fn(conc_out, conc_label)
    return val_loss.data

def plot_ae_outputs(sTitle, encoder,decoder,n=10):
    plt.figure(num=sTitle, figsize=(16,4.5))
    targets = test_dataset.targets.numpy()
    t_idx = {i:np.where(targets==i)[0][0] for i in range(n)}
    for i in range(n):
      ax = plt.subplot(2,n,i+1)
      img = test_dataset[t_idx[i]][0].unsqueeze(0).to(device)
      encoder.eval()
      decoder.eval()
      with torch.no_grad():
         rec_img  = decoder(encoder(img))
      plt.imshow(img.cpu().squeeze().numpy(), cmap='gist_gray')
      ax.get_xaxis().set_visible(False)
      ax.get_yaxis().set_visible(False)
      if i == n//2:
        ax.set_title('Original images')
      ax = plt.subplot(2, n, i + 1 + n)
      plt.imshow(rec_img.cpu().squeeze().numpy(), cmap='gist_gray')
      ax.get_xaxis().set_visible(False)
      ax.get_yaxis().set_visible(False)
      if i == n//2:
         ax.set_title('Reconstructed images')
    plt.show()

loss_fn = torch.nn.MSELoss()
lr= 0.001

# Set latent space dimension
d = 4

encoder_4d = Encoder(encoded_space_dim=d,fc2_input_dim=128)
decoder_4d = Decoder(encoded_space_dim=d,fc2_input_dim=128)
params_to_optimize = [
    {'params': encoder_4d.parameters()},
    {'params': decoder_4d.parameters()}
]

optim = torch.optim.Adam(params_to_optimize, lr=lr, weight_decay=1e-05)

# Check if the GPU is available
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
print(f'Selected device: {device}')

# Move both the encoder and the decoder to the selected device
encoder_4d.to(device)
decoder_4d.to(device)

sTitle = "4 Dimensions"
print(sTitle)
num_epochs = 30
loss_map_4d = {'train_loss':[],'val_loss':[]}
for epoch in range(num_epochs):
   train_loss =train_epoch(encoder_4d,decoder_4d,device,
   train_loader,loss_fn,optim)
   val_loss = test_epoch(encoder_4d,decoder_4d,device,test_loader,loss_fn)
   print('\n EPOCH {}/{} \t train loss {} \t val loss {}'.format(epoch + 1, num_epochs,train_loss,val_loss))
   loss_map_4d['train_loss'].append(train_loss)
   loss_map_4d['val_loss'].append(val_loss)
   #plot_ae_outputs(sTitle, encoder_4d,decoder_4d,n=10)

loss_fn = torch.nn.MSELoss()
lr= 0.001

torch.manual_seed(0)

d = 5

encoder_5d = Encoder(encoded_space_dim=d,fc2_input_dim=128)
decoder_5d = Decoder(encoded_space_dim=d,fc2_input_dim=128)
params_to_optimize = [
    {'params': encoder_5d.parameters()},
    {'params': decoder_5d.parameters()}
]

optim = torch.optim.Adam(params_to_optimize, lr=lr, weight_decay=1e-05)

# Check if the GPU is available
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
print(f'Selected device: {device}')

# Move both the encoder and the decoder to the selected device
encoder_5d.to(device)
decoder_5d.to(device)

sTitle = "5 Dimensions"
print(sTitle)
num_epochs = 30
loss_map_5d = {'train_loss':[],'val_loss':[]}
for epoch in range(num_epochs):
   train_loss =train_epoch(encoder_5d,decoder_5d,device,
   train_loader,loss_fn,optim)
   val_loss = test_epoch(encoder_5d,decoder_5d,device,test_loader,loss_fn)
   print('\n EPOCH {}/{} \t train loss {} \t val loss {}'.format(epoch + 1, num_epochs,train_loss,val_loss))
   loss_map_5d['train_loss'].append(train_loss)
   loss_map_5d['val_loss'].append(val_loss)
   #plot_ae_outputs(sTitle, encoder_5d,decoder_5d,n=10)

loss_fn = torch.nn.MSELoss()
lr= 0.001

torch.manual_seed(0)

d = 6

encoder_6d = Encoder(encoded_space_dim=d,fc2_input_dim=128)
decoder_6d = Decoder(encoded_space_dim=d,fc2_input_dim=128)
params_to_optimize = [
    {'params': encoder_6d.parameters()},
    {'params': decoder_6d.parameters()}
]

optim = torch.optim.Adam(params_to_optimize, lr=lr, weight_decay=1e-05)

# Check if the GPU is available
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
print(f'Selected device: {device}')

# Move both the encoder and the decoder to the selected device
encoder_6d.to(device)
decoder_6d.to(device)

sTitle = "6 Dimensions"
print(sTitle)
num_epochs = 30
loss_map_6d = {'train_loss':[],'val_loss':[]}
for epoch in range(num_epochs):
   train_loss =train_epoch(encoder_6d,decoder_6d,device,
   train_loader,loss_fn,optim)
   val_loss = test_epoch(encoder_6d,decoder_6d,device,test_loader,loss_fn)
   print('\n EPOCH {}/{} \t train loss {} \t val loss {}'.format(epoch + 1, num_epochs,train_loss,val_loss))
   loss_map_6d['train_loss'].append(train_loss)
   loss_map_6d['val_loss'].append(val_loss)
   #plot_ae_outputs(sTitle, encoder_6d,decoder_6d,n=10)

loss_fn = torch.nn.MSELoss()
lr= 0.001

torch.manual_seed(0)

d = 7

encoder_7d = Encoder(encoded_space_dim=d,fc2_input_dim=128)
decoder_7d = Decoder(encoded_space_dim=d,fc2_input_dim=128)
params_to_optimize = [
    {'params': encoder_7d.parameters()},
    {'params': decoder_7d.parameters()}
]

optim = torch.optim.Adam(params_to_optimize, lr=lr, weight_decay=1e-05)

# Check if the GPU is available
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
print(f'Selected device: {device}')

# Move both the encoder and the decoder to the selected device
encoder_7d.to(device)
decoder_7d.to(device)

sTitle = "7 Dimensions"
print(sTitle)
num_epochs = 30
loss_map_7d = {'train_loss':[],'val_loss':[]}
for epoch in range(num_epochs):
   train_loss =train_epoch(encoder_7d,decoder_7d,device,
   train_loader,loss_fn,optim)
   val_loss = test_epoch(encoder_7d,decoder_7d,device,test_loader,loss_fn)
   print('\n EPOCH {}/{} \t train loss {} \t val loss {}'.format(epoch + 1, num_epochs,train_loss,val_loss))
   loss_map_7d['train_loss'].append(train_loss)
   loss_map_7d['val_loss'].append(val_loss)
   #plot_ae_outputs(sTitle, encoder_7d,decoder_7d,n=10)

loss_fn = torch.nn.MSELoss()
lr= 0.001

torch.manual_seed(0)

d = 8

encoder_8d = Encoder(encoded_space_dim=d,fc2_input_dim=128)
decoder_8d = Decoder(encoded_space_dim=d,fc2_input_dim=128)
params_to_optimize = [
    {'params': encoder_8d.parameters()},
    {'params': decoder_8d.parameters()}
]

optim = torch.optim.Adam(params_to_optimize, lr=lr, weight_decay=1e-05)

# Check if the GPU is available
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
print(f'Selected device: {device}')

# Move both the encoder and the decoder to the selected device
encoder_8d.to(device)
decoder_8d.to(device)

sTitle = "8 Dimensions"
print(sTitle)
num_epochs = 30
loss_map_8d = {'train_loss':[],'val_loss':[]}
for epoch in range(num_epochs):
   train_loss =train_epoch(encoder_8d,decoder_8d,device,
   train_loader,loss_fn,optim)
   val_loss = test_epoch(encoder_8d,decoder_8d,device,test_loader,loss_fn)
   print('\n EPOCH {}/{} \t train loss {} \t val loss {}'.format(epoch + 1, num_epochs,train_loss,val_loss))
   loss_map_8d['train_loss'].append(train_loss)
   loss_map_8d['val_loss'].append(val_loss)
   #plot_ae_outputs(sTitle, encoder_8d,decoder_8d,n=10)

x = [i for i in range(30)]
fig, ax = plt.subplots(3,2, figsize=(15,15))
ax[0,0].plot(x, loss_map_4d['train_loss'], label="Train loss")
ax[0,0].plot(x, loss_map_4d['val_loss'], label="Val loss")
ax[0,0].set_title("4 Dimensional Latent Space, 30 Epochs")
ax[0,0].legend(loc='upper right')

ax[0,1].plot(x, loss_map_5d['train_loss'], label="Train loss")
ax[0,1].plot(x, loss_map_5d['val_loss'], label="Val loss")
ax[0,1].set_title("5 Dimensional Latent Space, 30 Epochs")
ax[0,1].legend(loc='upper right')

ax[1,0].plot(x, loss_map_6d['train_loss'], label="Train loss")
ax[1,0].plot(x, loss_map_6d['val_loss'], label="Val loss")
ax[1,0].set_title("6 Dimensional Latent Space, 30 Epochs")
ax[1,0].legend(loc='upper right')

ax[1,1].plot(x, loss_map_7d['train_loss'], label="Train loss")
ax[1,1].plot(x, loss_map_7d['val_loss'], label="Val loss")
ax[1,1].set_title("7 Dimensional Latent Space, 30 Epochs")
ax[1,1].legend(loc='upper right')

ax[2,1].plot(x, loss_map_8d['train_loss'], label="Train loss")
ax[2,1].plot(x, loss_map_8d['val_loss'], label="Val loss")
ax[2,1].set_title("8 Dimensional Latent Space, 30 Epochs")
ax[2,1].legend(loc='upper right')

plot_ae_outputs("4 Dimensions", encoder_4d,decoder_4d,n=10)
plot_ae_outputs("5 Dimensions", encoder_5d,decoder_5d,n=10)
plot_ae_outputs("6 Dimensions", encoder_6d,decoder_6d,n=10)
plot_ae_outputs("7 Dimensions", encoder_7d,decoder_7d,n=10)
plot_ae_outputs("8 Dimensions", encoder_8d,decoder_8d,n=10)
