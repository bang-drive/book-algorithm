from absl import app, flags, logging
import torch
import torchvision

# Save to <data_dir>/<label>/.../YYMMDD_HHMMSS_MS.jpg
flags.DEFINE_string('data_dir', None, 'Directory to load images.')
flags.mark_flag_as_required('data_dir')


EPOCHS = 13
BATCH_SIZE = 16


def main(argv):
    dataset = torchvision.datasets.ImageFolder(
        flags.FLAGS.data_dir,
        transform=torchvision.transforms.Compose([
            torchvision.transforms.Resize((224, 224)),
            torchvision.transforms.ToTensor()]))
    train_size = int(0.8 * len(dataset))
    train_data, test_data = torch.utils.data.random_split(
        dataset, [train_size, len(dataset) - train_size])
    train_loader = torch.utils.data.DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_data, batch_size=BATCH_SIZE, shuffle=True)

    model = torchvision.models.resnet18(weights='DEFAULT')
    model.train()
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(EPOCHS):
        for images, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        logging.info(f'Epoch {epoch}, loss: {loss.item()}')

    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    logging.info(f'Accuracy: {correct / total}')


if __name__ == '__main__':
    app.run(main)
