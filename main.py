import api
import dataset
import detect


def main():
    if not api.is_service_alive():
        print("Perch Mount System 異常，請確認服務狀態！")
        return

    undetected_media = api.get_undetected_media()
    image_dataset, video_dataset = dataset.to_image_and_video_dataset(undetected_media)
    image_loader, video_loader = detect.datasets_to_loaders(
        image_dataset, video_dataset
    )

    detected_images = detect.detect_images(image_loader)
    detected_videos = detect.detect_videos(video_loader)

    api.upload_detected_media(detected_images + detected_videos)


if __name__ == "__main__":
    main()
