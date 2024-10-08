import os
import pprint

from absl import app, flags, logging
import torch
import torchvision

from bang.end2end.common import count_subdir_files


# Save to <data_dir>/<label>/.../YYMMDD_HHMMSS_MS.jpg
flags.DEFINE_string('data_dir', None, 'Directory to load images.')
flags.mark_flag_as_required('data_dir')


EPOCHS = 10
BATCH_SIZE = 16


def main(argv):
    # Data
    logging.info('Train from data:')
    pprint.pprint(count_subdir_files(flags.FLAGS.data_dir))

    dataset = torchvision.datasets.ImageFolder(
        flags.FLAGS.data_dir,
        transform=torchvision.transforms.Compose([
            torchvision.transforms.Resize((224, 224)),
            torchvision.transforms.ToTensor()]))
    train_size = int(0.9 * len(dataset))
    train_data, test_data = torch.utils.data.random_split(
        dataset, [train_size, len(dataset) - train_size])
    train_loader = torch.utils.data.DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_data, batch_size=BATCH_SIZE, shuffle=True)

    # Model
    model = torchvision.models.resnet18(weights='DEFAULT')
    model.fc = torch.nn.Linear(512, 3)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # Train
    for epoch in range(EPOCHS):
        model.train()
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
        logging.info(f'Epoch {epoch}, loss: {loss.item()}')

    # Test
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    logging.info(f'Accuracy: {correct / total}')
    torch.save(model, os.path.join(os.path.dirname(__file__), 'model.pt'))


if __name__ == '__main__':
    app.run(main)
