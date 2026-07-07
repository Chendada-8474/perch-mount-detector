import os

import cv2
import envs
from torch.utils.data import Dataset
import torchvision.io
from PIL import Image


def to_image_and_video_dataset(media: list[dict]):
    images = []
    videos = []
    for medium in media:
        if medium["medium_type"] == "image":
            images.append(medium)
        else:
            videos.append(medium)
    return ImageDataset(images), VideoDataset(videos)


class MediumDataset(Dataset):

    def __init__(self, task: list) -> None:
        self.task = task
        super().__init__()

    def __len__(self):
        return len(self.task)


class ImageDataset(MediumDataset):
    def __getitem__(self, index):
        try:
            img = Image.open(
                os.path.join(envs.MEDIA_DIR, self.task[index]["s3_file_name"])
            ).convert("RGB")

        except Exception as e:
            print(e)
            img = None
        return img, self.task[index]


class VideoDataset(MediumDataset):
    def __init__(self, task: list, interval=3) -> None:
        self.interval = interval
        super().__init__(task)

    def __getitem__(self, index):

        current_task = self.task[index]
        try:
            video_path = os.path.join(envs.MEDIA_DIR, current_task["s3_file_name"])

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError(f"無法開啟影片: {video_path}")

            fps = cap.get(cv2.CAP_PROP_FPS)
            interval_frames = max(1, int(self.interval * (fps if fps > 0 else 30)))

            pil_frames = []
            current_frame_index = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if current_frame_index % interval_frames == 0:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_frames.append(Image.fromarray(frame_rgb))

                current_frame_index += 1

            cap.release()

            if not pil_frames:
                raise ValueError("影片中沒有擷取到任何影格")

            return pil_frames, current_task

        except Exception as e:
            print(f"影片讀取失敗 (index {index}): {e}")
            return None, current_task
