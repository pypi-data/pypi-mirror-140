#!/usr/bin/python
# encoding=utf-8
from loguru import logger

from monitors.page.classifier import SVMClassifier
from monitors.page.cutter import VideoCutter
from monitors.page.reporter import Reporter


def cut(video_path, cut_result):
    """
    采集训练集
    :param video_path:video_path = '../../demo.mp4'
    :param cut_result: './cut_result'
    :return:
    """

    # --- cut ---
    cutter = VideoCutter()
    res = cutter.cut(video_path)
    stable, unstable = res.get_range()

    res.pick_and_save(
        stable,
        # 每段区间的采样数，5即每个阶段等距离截取5张图片
        5,
        # 采样结果保存的位置
        cut_result,
    )


def train(data_home):
    """
    这个例子描述了如何训练一个后续可用的模型
    在 cut 流程之后，你应该能得到一个已经分拣好的训练集文件夹
    我们将基于此文件夹进行模型的训练

    :param data_home: DATA_HOME = './cut_result'
    :return:
    """

    cl = SVMClassifier()

    # 加载数据
    cl.load(data_home)
    # 在加载数据完成之后需要先训练
    cl.train()
    # 在训练后你可以把模型保存起来
    cl.save_model('model.pkl')


def predict(target_video, model_path):
    """
    利用训练好的模型，建立长期的视频分析工作流
    在 train.py 之后，你应该能得到一个 model.pkl 模型
    :param target_video: TARGET_VIDEO = '../../demo.mp4'
    :param model_path: './model.pkl'
    :return:
    """
    logger.info('------------ Start analyzing video！------------- ')

    # cut
    # 这里依旧使用了 cut，主要目的还是为了可以比较好的处理变化中的过程
    # 但这次我们不需要用到 pick_and_save，因为这次 classifier 不会使用 cutter 的数据
    cutter = VideoCutter()
    res = cutter.cut(target_video)
    stable, _ = res.get_range()

    # classify
    # 这里的参数需要保持与train.py一致，如果你有改动的话
    cl = SVMClassifier()
    cl.load_model(model_path)

    classify_result = cl.classify(
        target_video,
        stable,
    )

    r = Reporter()
    r.draw(
        classify_result,
        report_path='report.html',
        cut_result=res,
    )
    return classify_result.to_dict()

