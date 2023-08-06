#!/usr/bin/python
# encoding=utf-8
from loguru import logger

from monitors.page.cutter import VideoCutter
from monitors.page.classifier.keras import KerasClassifier
from monitors.page.reporter import Reporter
from monitors.page.video import VideoObject


def cut(video_path, data_home):
    """

    :param video_path: video_path = "../videos/douyin1.mp4"
    :param data_home: data_home = "./dataset"
    :return:
    """

    video = VideoObject(video_path)
    video.load_frames()

    cutter = VideoCutter()
    res = cutter.cut(video)
    stable, unstable = res.get_range(offset=3)

    # save dataset
    res.pick_and_save(stable, 10, to_dir=data_home, meaningful_name=True)
    print(f"data saved to {data_home}")


def train(data_home, loop):
    """

    :param loop: 训练循环次数
    :param data_home: data_home = "./dataset"
    :return:
    """

    model_file = "./keras_model.h5"

    cl = KerasClassifier(
        # 轮数
        epochs=int(loop),
        # 保证数据集的分辨率统一性
        target_size=(888, 1920),
    )
    cl.train(data_home)
    cl.save_model(model_file, overwrite=True)


def predict(video_path, model_file):
    """

    :param video_path: video_path = "../videos/test.mp4"
    :param model_file: model_file = "./keras_model.h5"
    :return:
    """
    logger.info('------------ Start analyzing video！------------- ')

    video = VideoObject(video_path)
    video.load_frames()

    # --- cutter ---
    cutter = VideoCutter()
    res = cutter.cut(video)
    stable, unstable = res.get_range()

    # --- classifier ---
    cl = KerasClassifier(
        # 在使用时需要保证数据集格式统一（与训练集）
        # 因为 train_model.py 用了 600x800，所以这里设定成一样的
        target_size=(888, 1920),
    )

    cl.load_model(model_file)

    classify_result = cl.classify(video, stable, keep_data=True)
    result_dict = classify_result.to_dict()

    # --- draw ---
    r = Reporter()
    r.draw(classify_result, report_path='report.html')
    return result_dict
