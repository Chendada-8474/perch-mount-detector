# PERCH MOUNT DETECTOR



建議用 [s3fuse](https://github.com/s3fs-fuse/s3fs-fuse) 把 bucket 掛到你要的地方，然後修改 `envs.py` 裡的 `MEDIA_DIR` 變數，讓系統直接去讀取 s3。

去下載 [`custom_detectivekite.pt`](https://drive.google.com/file/d/1riASXfqm4imRT0IlX6WQVDT4B3-k1A9z/view?usp=drive_link) 放到專案目錄下。