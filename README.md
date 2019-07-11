# Cappi
Raspberry Piで動作する動体検知カメラ。
カメラで取得したフレーム内に動いている物体がある間だけ動画を記録し、動いている物体がいなくなると動画を保存します。
プログラムにはOpenCVとPicameraを使用します。

## 動作環境
- Raspberry Pi 3 Model B+
- Raspberry Pi Camera Module V2
- Raspbian 9.8 (Stretch)
- Python 3.5.3
- OpenCV 3.4.5
- Picamera

## 機能
- カメラで取得したフレーム内に動いている物体がある間、動画を記録する
- 動いている物体がいなくなると動画の記録を終了・保存する

## 使い方
```
$ python3 cappi.py
```
