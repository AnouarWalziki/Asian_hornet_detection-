# -*- coding: utf-8 -*-
"""frelon_cnn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fyiSBVyF-Py4TEAg7NRRFhNEgYbofNNd
"""

from google.colab import drive
drive.mount('/content/drive')

import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import os


transform = torchvision.transforms.Compose([
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Resize((300,225)),
    torchvision.transforms.Normalize(mean=[0.5,0.5,0.5], std=[0.5,0.5,0.5],),
    ])

num_training_data = 2886
dataset_images = torch.zeros((num_training_data,3,300,225))
dataset_classes = torch.zeros((num_training_data))

i = 0


for filename in os.listdir('/content/drive/MyDrive/imgs_frelon/imgs_train/absence'):
    img = mpimg.imread('/content/drive/MyDrive/imgs_frelon/imgs_train/absence/'+filename)
    if img is not None:
        img = transform(img)
        dataset_images[i] = img
        dataset_classes[i] = 1
        i+=1
        print(i)

for filename in os.listdir('/content/drive/MyDrive/imgs_frelon/imgs_train/presence'):
    img = mpimg.imread('/content/drive/MyDrive/imgs_frelon/imgs_train/presence/'+filename)
    if img is not None:
        img = transform(img)
        dataset_images[i] = img
        dataset_classes[i] = 0
        i+=1
        print(i)
        
# Hyper parameters
batch_size = 64
learning_rate = 0.005
beta = 0.95
num_epochs = 20

training_dataset = torch.utils.data.TensorDataset(dataset_images, dataset_classes)

train_loader = torch.utils.data.DataLoader(training_dataset, batch_size = batch_size, shuffle = True)



data_iter = iter(train_loader)

images, labels = data_iter.next()

print(images.shape)
print(labels.shape)


  
#print(dataset_images.shape)
#print(dataset_classes.shape)

#%%Testing

def validation(test_loader, model):
    # Test the model
    model.eval()
    # In test phase, we don't need to compute gradients (for memory efficiency)
    with torch.no_grad():
        correct = 0
        total = 0
        for images, labels in test_loader:

            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    return (correct, total)

num_testing_data = 720
dataset_images_test = torch.zeros((num_testing_data,3,300,225))
dataset_classes_test = torch.zeros((num_testing_data))

j =0
for filename in os.listdir('/content/drive/MyDrive/imgs_frelon/imgs_test/absence' ):
    img = mpimg.imread('/content/drive/MyDrive/imgs_frelon/imgs_test/absence/' +filename)
    if img is not None:
        img = transform(img)
        dataset_images_test[j] = img
        dataset_classes_test[j] = 1
        j+=1
        print(j)

for filename in os.listdir('/content/drive/MyDrive/imgs_frelon/imgs_test/presence' ):
    img = mpimg.imread('/content/drive/MyDrive/imgs_frelon/imgs_test/presence/' +filename)
    if img is not None:
        img = transform(img)
        dataset_images_test[j] = img
        dataset_classes_test[j] = 0
        j+=1
        print(j)

test_dataset = torch.utils.data.TensorDataset(dataset_images_test, dataset_classes_test)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size = batch_size, shuffle = False)

#%%Importing pretrained model

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
model = torchvision.models.resnet18(pretrained=True)


for param in model.parameters():
    param.requires_grad = False

model.fc = nn.Linear(model.fc.in_features, 2)
model = model.to(device)

#%% Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate , momentum=beta)

#%% Train the model
num_batch = len(train_loader) #600 batches each containing 100 images = 60000 images
training_loss_v = []
valid_acc_v = []
for epoch in range(num_epochs):
    loss_tot = 0
    for i, (images, labels) in enumerate(train_loader):
        images = images.to(device)
        labels = labels.to(device).type(torch.LongTensor)

        
        # Forward pass
        outputs = model(images)
        _, preds = torch.max(outputs, 1)
        #print(outputs.shape)
        #print(outputs)
        #outputs = torch.argmax(outputs, dim=1)
        #print(outputs)
        #print(labels)
        loss = criterion(outputs, labels)
        
        # Backward and optimize
        optimizer.zero_grad() #set gradients of all parameters to zero
        loss.backward()
        optimizer.step()
        
        loss_tot += loss.item()
        if (i+1) % 20== 0:
            print ('Epoch [{}/{}], Step [{}/{}], Batch Loss: {:.4f}' 
                   .format(epoch+1, num_epochs, i+1, num_batch, loss.item()/len(labels)))
         
       #Validation     
    (correct, total) = validation(test_loader, model)
    print ('Epoch [{}/{}], Training Loss: {:.4f}, Valid Acc: {} %'
           .format(epoch+1, num_epochs, loss_tot/num_training_data, 100 * correct / total))
    training_loss_v.append(loss_tot/num_training_data)
    valid_acc_v.append(correct / total)

# Commented out IPython magic to ensure Python compatibility.
# %% Save the model checkpoint
# torch.save(model.state_dict(), 'model.ckpt')
# 
# #%% plot results
# plt.figure(2)
# plt.clf()
# plt.plot(np.array(training_loss_v),'r',label='Training loss')
# plt.legend()
# 
# plt.figure(3)
# plt.clf()
# plt.plot(np.array(valid_acc_v),'g',label='Validation accuracy')
# plt.legend()