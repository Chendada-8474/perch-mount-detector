import torch
import datetime
import envs
from collections import defaultdict, Counter

model = torch.hub.load(
    "ultralytics/yolov5",
    "custom",
    path="./custom_detectivekite.pt",
)
model.conf = 0.50


def _detect(data) -> list[dict]:
    results = model(data).pandas().xyxy
    return [result.to_dict(orient="records") for result in results]


def _class_to_taxa_order(class_by_model: int) -> int:
    return envs.TAXON_ORDER_TRANS_CUS_DK[class_by_model]


def custom_collate_fn(batch):
    valid_batch = [item for item in batch if item is not None]

    if len(valid_batch) == 0:
        return [], []

    images, infos = zip(*valid_batch)

    return list(images), list(infos)


def datasets_to_loaders(image_dataset, video_dataset):
    image_loader = torch.utils.data.DataLoader(
        image_dataset,
        batch_size=2,
        num_workers=0,
        collate_fn=custom_collate_fn,
    )

    video_loader = torch.utils.data.DataLoader(
        video_dataset,
        batch_size=1,
        num_workers=0,
        collate_fn=custom_collate_fn,
    )
    return image_loader, video_loader


def detect_images(image_loader):
    results = []
    for images, metas in image_loader:
        detecteds = _detect(images)
        current_datetime = datetime.datetime.now().isoformat()
        for image, meta, detected in zip(images, metas, detecteds):
            width, height = image.size
            results.append(
                {
                    "id": meta["id"],
                    "detected_at": current_datetime,
                    "individuals": [
                        {
                            "taxon_order_by_ai": _class_to_taxa_order(
                                box["class"],
                            ),
                            "xmin": box["xmin"] / width,
                            "ymin": box["ymin"] / height,
                            "xmax": box["xmax"] / width,
                            "ymax": box["ymax"] / height,
                            "confidence": box["confidence"],
                        }
                        for box in detected
                    ],
                }
            )
    return results


def detect_videos(video_loader):
    results = []

    for batch_frames, batch_meta in video_loader:
        frames = batch_frames[0]
        meta = batch_meta[0]
        detected = _detect(frames)
        current_datetime = datetime.datetime.now().isoformat()
        summarized_results = _summarize_detections(detected)

        results.append(
            {
                "id": meta["id"],
                "detected_at": current_datetime,
                "individuals": [
                    {
                        "taxon_order_by_ai": _class_to_taxa_order(
                            summarized_result["class"],
                        ),
                        "confidence": summarized_result["confidence"],
                    }
                    for summarized_result in summarized_results
                ],
            }
        )

    return results


def _summarize_detections(data_list):
    conf_sum = defaultdict(float)
    box_count = defaultdict(int)
    max_per_image = Counter()

    for boxes in data_list:
        for box in boxes:
            conf_sum[box["class"]] += box["confidence"]
            box_count[box["class"]] += 1
        counts = Counter((box["class"] for box in boxes))
        max_per_image |= counts

    summary = []

    for class_, count in max_per_image.items():
        for _ in range(count):
            summary.append(
                {"class": class_, "confidence": conf_sum[class_] / box_count[class_]}
            )

    return summary
