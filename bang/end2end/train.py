import torch
import torchvision

# Save to <data_dir>/<label>/.../YYMMDD_HHMMSS_MS.jpg
# flags.DEFINE_string('data_dir', '.', 'Directory to save images.')

DATA_DIR = '/home/disk/bang/end2end/.sampling'
# Use ImageFolder to load data from DATA_DIR and train a model based on ResNet18.
dataset = torchvision.datasets.ImageFolder(DATA_DIR, transform=torchvision.transforms.Compose([
    torchvision.transforms.Resize((224, 224)),
    torchvision.transforms.ToTensor()
]))
loader = torch.utils.data.DataLoader(dataset, batch_size=4, shuffle=True)

model = torchvision.models.resnet18(pretrained=True)
model.fc = torch.nn.Linear(512, 3)
model = model.cuda()

criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(10):
    for images, labels in loader:
        images = images.cuda()
        labels = labels.cuda()
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
    print(F'Epoch {epoch} loss: {loss.item()}')
