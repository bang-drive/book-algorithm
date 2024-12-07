import io
import os
import threading

from absl import app, logging
from PIL import Image
import torch
import torchvision

from bang.common.timer import RecurringTimer
from bang.common.topic import Topic


CONTROL_FREQUENCY = 10
CONTROL_MAX = 32768
STEER_VALUES = {
    'LEFT': -CONTROL_MAX,
    'RIGHT': CONTROL_MAX,
    'STRAIGHT': 0,
}
CURRENT_STEER = 'STRAIGHT'


def camera_receiver():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = torch.load(os.path.join(os.path.dirname(__file__), 'model.pt'))
    model.to(device)
    model.eval()
    output_to_steer = {
        0: 'STRAIGHT',
        1: 'LEFT',
        2: 'RIGHT',
    }

    transform = torchvision.transforms.Compose([
        torchvision.transforms.Resize((224, 224)),
        torchvision.transforms.ToTensor()])

    global CURRENT_STEER
    for message in Topic.subscribe(Topic.CAMERA):
        image = Image.open(io.BytesIO(message))
        # Mask off a rectangle at position (395, 520) and size (234, 56) which is the main car
        # itself.
        image.paste((0, 0, 0), (395, 520, 395 + 234, 520 + 56))
        # Cut the image to the lower half.
        w, h = image.size
        image = image.crop((0, h // 2, w, h))
        image = transform(image).unsqueeze(0).to(device)
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)
        CURRENT_STEER = output_to_steer[predicted.item()]


def control_publisher():
    global CURRENT_STEER
    timer = RecurringTimer(1.0 / CONTROL_FREQUENCY)
    while timer.wait():
        Topic.publish(Topic.CONTROL, {
            'source': 'end2end',
            'pedal': CONTROL_MAX,
            'steer': STEER_VALUES[CURRENT_STEER],
        })
        logging.info(CURRENT_STEER)


def main(argv):
    threading.Thread(target=camera_receiver).start()
    threading.Thread(target=control_publisher).start()


if __name__ == '__main__':
    app.run(main)
