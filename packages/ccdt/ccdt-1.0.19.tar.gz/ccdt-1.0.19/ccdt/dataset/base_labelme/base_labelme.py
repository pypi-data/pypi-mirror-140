# -*- coding: utf-8 -*-
# @Time : 2022/2/18 18:01
# @Author : Zhan Yong
import os
from ..utils import path
import json
import collections
import cv2
# import cv2
import numpy as np
from tqdm import *
import shutil
import warnings
import prettytable as pt
from ..utils import Encoder
import copy
from functools import wraps
import multiprocessing
from functools import reduce


# 定义类时，在没有确切的继承之前，默认继承object。python3默认继承object，如此定义可以在python2和python3下运行。


class BaseLabelme(object):

    @property
    def num_labelme(self):
        return len(self.labelme_paths)

    @property
    def num_images(self):
        return len(self.images_paths)

    @property
    def num_label(self):
        return len(self.label_name)

    @property
    def num_shape_type(self):
        try:
            self.shape_type
        except Exception as e:
            print(e)
            return None
        return len(self.shape_type)

    @property
    def num_background(self):
        return len(self.background)

    @property
    def num_flags(self):
        return len(self.flags)

    def __update_property__(self):
        """
        统计，图片文件个数，labelme文件个数，标注形状个数，背景图片个数，标注类别个数
        """
        self.label_name = list()
        self.background = list()
        self.labelme_paths = list()
        self.images_paths = list()
        self.flags = dict()
        self.flags_name = list()
        self.flags_key_name = list()
        self.shape_type = list()
        self.shape_type_name = list()
        self.label_flags_shape_name = list()
        self.label_shape_flags = dict()
        self.flags_key = list()
        for data_info in self.data_infos:
            # print(data_info)
            try:
                image_path = os.path.join(data_info['image_dir'], data_info['image_file'])
            except Exception as e:
                print(e)
                print(data_info)
                print('json文件存在，但图片文件不存在请检查数据')
                # a = os.path.join(data_info['labelme_dir'], data_info['labelme_file'])
                # print(a)
                # os.remove(a)
                continue
            if data_info['labelme_file']:
                json_path = os.path.join(data_info['labelme_dir'], data_info['labelme_file'])
                self.labelme_paths.append(json_path)
            else:
                json_path = None
            self.images_paths.append(image_path)
            if json_path:
                # data_info['labelme_info'] 直接内存中获取，不用读取文件
                # with open(json_path, 'r', encoding='UTF-8') as labelme_fp:
                # labelme_info = json.load(labelme_fp)
                # 直接从内存中进行获取操作
                if data_info['labelme_info']['shapes']:
                    for shape in data_info['labelme_info']['shapes']:
                        flags_shape = dict()
                        for key, value in shape.items():
                            if key == 'label':
                                if value not in self.label_shape_flags.keys():
                                    self.label_shape_flags[value] = flags_shape
                            if key == 'shape_type':
                                # for i in self.label_shape_flags.keys():
                                #     if shape['label'] == i:
                                #         self.shape_type.append(value)
                                # if shape['label'] not in self.label_shape_flags.keys():
                                # if value not in self.shape_type:
                                if not self.label_shape_flags[shape['label']]:
                                    self.shape_type.append(value)
                                else:
                                    if shape['shape_type'] not in self.label_shape_flags[shape['label']]['shape_type']:
                                        self.shape_type.append(value)
                                flags_shape[key] = self.shape_type
                            if key == 'flags':
                                for flag in list(value):
                                    # if shape['flags'][flag] is True:
                                    if flag not in self.flags_key:
                                        self.flags_key.append(flag)
                                    flags_shape[key] = self.flags_key
                        self.flags.update(shape['flags'])
                else:
                    self.background.append(image_path)
                    # 默认没有背景类，有背景类把background设置为True
                    data_info['background'] = True
            else:
                self.background.append(image_path)
                data_info['background'] = True
        # {'活': True, '安全帽': True, '鞋子': True, '工装': True, '黑色': True, '帅': True}
        print(self.label_shape_flags)
        print()

    @classmethod
    def find(cls, image_file, data_infos):
        # 判断image_file 是否在data_infos里面，如果在就返回下标索引，如果不在返回None用于追加判断
        for index, info in enumerate(data_infos):
            # 如果多种数据集中存在相同的图片，则不能类别合并
            if info['image_file'] == image_file:
                return index
        return None

    def __repr__(self):
        """
        对象的字符串表示形式的内置方法，主要使用表格打印信息
        :return:
        """
        tb = pt.PrettyTable()
        tb.field_names = ['num_images', 'num_shape_type', 'num_label', 'num_labelme', 'num_background', 'num_flags']

        tb.add_row(
            [self.num_images, self.num_shape_type, self.num_label, self.num_labelme, self.num_background, self.num_flags])
        tb2 = pt.PrettyTable()
        # tb.set_style(pt.MSWORD_FRIENDLY)
        # tb2.field_names = ['label_name', 'flags_name']
        # tb2.add_row([self.label_name, self.flags_name])
        return str(tb)

    def __init__(self, labelme_dir, images_dir, only_annt=False, is_labelme=False):
        # print(only_annt)
        # print(labelme_dir)
        # print(images_dir)
        """
        类实例方法。称为构造方法。初始化方法。
        :param datasets: 传入处理数据集
        :param only_labelme: False默认处理labelme和图片，True只处理labelme
        """
        self.only_annt = only_annt
        self.labelme_dir = labelme_dir
        self.images_dir = images_dir

        # self.name_classes = list()
        # self.shape_type = list()
        # self.flags = dict()
        # self.background = list()
        # self.labelme_paths = list()
        # self.images_paths = list()

        # 标签统计
        # self.label = []

        self.data_infos = list()
        self.class2datainfo = collections.defaultdict(list)
        self.type2datainfo = collections.defaultdict(list)
        # 不同元素
        self.different = list()
        # 类别和形状筛选是否删除背景类条件，False不删除，True删除
        self.filter_empty = None
        # 如果处理labelme走if，如果是子类继承走else
        self.self_bak = None
        # 通过类别判断，是子类还是父类
        if type(self) == BaseLabelme or is_labelme:
            # self.datasets = self._check_dataset(datasets)
            self.data_paths = self.get_data_paths()
            self.data_infos = self.load_labelme()
        # 其它数据集处理逻辑，比如coco转labelme
        # labelme转coco不能走这个方法，怎么办
        else:
            self.self2labelme()
        # 在coco转labelme完成后，才调用它实现它，打印相关属性信息。保持成labelme后在读取文件进行属性统计操作，还是在内存中就行属性统计操作呐
        self.__update_property__()
        # 数据初始完成后进行深度拷贝一份
        self.self_bak = copy.deepcopy(self)

    def get_data_paths(self):
        """
        数据路径处理
        :return:
        """
        data_paths = list()
        # 传递图片路径并返回图片路径列表，通过字典键（dataset['images_dir']）取到字典列表
        images_name_list = path.get_valid_paths(self.images_dir, ['.png', '.jpg', '.jpeg', '.tiff', '.psd', '.JPEG'])
        if len(images_name_list) == 0:
            print(self.images_dir + ': images图像数目={}'.format(len(images_name_list)))
        images_name_dict = dict()
        if not self.only_annt:
            for image_name in images_name_list:
                image_path = os.path.join(self.images_dir, image_name)
                # print(image_path)
                img_prefix, img_suffix = os.path.splitext(image_name)[-2], os.path.splitext(image_name)[-1]
                images_name_dict[img_prefix] = img_suffix
                #
                # self.images_paths.append(image_path)

        labelme_name_list = path.get_valid_paths(self.labelme_dir, ['.json'])
        labelme_name_dict = dict()
        for json_name in labelme_name_list:
            json_path = os.path.join(self.labelme_dir, json_name)
            # print(json_path)
            json_prefix, json_suffix = os.path.splitext(json_name)[-2], os.path.splitext(json_name)[-1]
            labelme_name_dict[json_prefix] = json_suffix
            #
            # self.labelme_paths.append(json_path)
        # print('Labelme 数据集图像:%s' % self.images_dir, '共%d张图像' % len(images_name_list),
        #       'Labelme 数据集注释:%s' % self.labelme_dir, '共%d个labelme注释文件' % len(labelme_name_list))

        # 针对没有图片或者没有labelme的文件夹，是否需要不执行？有图片，没有对应的labelme是允许的
        # assert len(images_name_list) and len(labelme_name_list), \
        # '{} 没有图片，\n{} 没有labelme'.format(self.labelme_dir, self.images_dir)

        # 把字典转list后合并成一个list,并去重。同时，集合转列表，然后再排序
        names = list(set(list(images_name_dict.keys()) + list(labelme_name_dict.keys())))
        names.sort()
        for name in names:
            data_path = dict(image_dir=self.images_dir,
                             image_file=name + images_name_dict[name] if images_name_dict.get(name,
                                                                                              False) else None,
                             labelme_dir=self.labelme_dir,
                             labelme_file=name + labelme_name_dict[name] if labelme_name_dict.get(name,
                                                                                                  False) else None)
            assert (data_path['labelme_file'] is not None) or (data_path['image_file'] is not None), \
                '{} 没有图片，\n{} 没有labelme'.format(data_path['labelme_dir'], data_path['image_dir'])
            data_paths.append(data_path)
        return data_paths

    def load_labelme(self):
        """
        读取labelme并统计背景类，有图片没有labelme和有labelme没有shapes属性则算背景类
        :return:
        """
        data_infos = list()
        # print('=' * 150)
        print("处理labelme数据进度:")
        for data_path in tqdm(self.data_paths):
            data_info = dict(image_dir=None, image_file=None, labelme_dir=None, labelme_file=None, labelme_info=None,
                             background=False)
            # 如果labelme为空，就返回空并且不拼接
            labelme_path = os.path.join(data_path['labelme_dir'], data_path['labelme_file']) if data_path[
                'labelme_file'] else None
            image_path = os.path.join(data_path['image_dir'], data_path['image_file']) if data_path[
                'image_file'] else None
            # 图像个数和labelme个数是否有为0的
            data_info['image_dir'] = data_path['image_dir']
            data_info['labelme_dir'] = data_path['labelme_dir']
            data_info['image_file'] = data_path['image_file']

            # data[image_path.replace()]

            # 运行过程中突然网络断开，执行立即出错
            if labelme_path:
                with open(labelme_path, 'r', encoding='UTF-8') as labelme_fp:
                    labelme_info = json.load(labelme_fp)
                data_info['labelme_file'] = data_path['labelme_file']
                data_info['labelme_info'] = labelme_info
                if labelme_info['shapes']:
                    for shape in labelme_info['shapes']:
                        # if shape['label'] not in self.name_classes:
                        #     #
                        #     self.name_classes.append(shape['label'])
                        self.class2datainfo[shape['label']].append(data_info)
                        # if shape['shape_type'] not in self.shape_type:
                        #     #
                        #     self.shape_type.append(shape['shape_type'])
                        self.type2datainfo[shape['shape_type']].append(data_info)
                # else:  # 有labelme但shapes为空
                #     #
                #     self.background.append(data_path)
                #     # 默认没有背景类，有背景类把background设置为True
                #     data_info['background'] = True
            # else:  # 存在图片木有labelme
            #     #
            #     self.background.append(image_path)
            #     data_info['background'] = True
            data_infos.append(data_info)
        return data_infos

    def crop_rectangle(self, image, shape):
        """
        长方形截取计算过程
        :param image: 图像
        :param shape: 形状坐标
        :return:
        """
        h = image.shape[0]
        w = image.shape[1]
        # 把从任意角度标注兼容
        points = np.array(shape['points'])
        point_min, point_max = points.min(axis=0), points.max(axis=0)
        x1, y1 = int(max(0, min(point_min[0], w))), int(max(0, min(point_min[1], h)))
        x2, y2 = int(max(0, min(point_max[0], w))), int(max(0, min(point_max[1], h)))
        # y1:y2 x1:x2,针对负数框在图片的外面时截取不到,正常标注不会超出图片面积范围。max(0, min(x, img_info['width'])把负数变成0。np.clip(point_min)
        crop_obj = image[y1:y2, x1:x2]
        return crop_obj

    def crop_objs(self, out_dir, min_pixel=10, replaces={}, ):
        # def crop_objs(self, out_dir, min_pixel=10, replaces={}, labelme_pool, queue):
        """
        截取图像功能实现，一张图片画框多少，就扣多少，不管是否重叠
        :param labelme_pool:
        :param out_dir: 保存截取图像路径
        :param shapes_type:标注形状类型，比如rectangle(长方形)、circle(圆)、polygon(多边形)、line(线)
        :param min_pixel:保存截取图片最小像素设置
        :param replaces:替换路径，把不变的路径替换为空
        """
        # 抠图数量统计
        num_crop = list()
        global folder
        assert not self.only_annt, '传入的图片路径为空，不能进行图片截取：{}'.format(self.only_annt)
        assert isinstance(replaces, dict)
        print("截图图片进度:")
        gl_tmp_out_dir: str = ''
        for data_info in tqdm(self.data_infos):
            labelme_path = os.path.join(data_info['labelme_dir'], data_info['labelme_file']) if data_info[
                'labelme_file'] else None
            image_path = os.path.join(data_info['image_dir'], data_info['image_file']) if data_info[
                'image_file'] else None
            # 只有labelme没有图片的时候不截取,直接跳过
            if (image_path is None) or (labelme_path is None):
                continue
            image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), 1)
            img_prefix, img_suffix = os.path.splitext(data_info['image_file'])[-2], \
                                     os.path.splitext(data_info['image_file'])[-1]
            num_obj = 0
            for old, new in replaces.items():
                replace_image_path = data_info['image_dir'].replace(old, new)
                # 3. 去掉开头的 斜杠
                remove_slash = replace_image_path.strip('\\/')
                gl_tmp_out_dir = os.path.join(out_dir, remove_slash)
                folder = remove_slash.split('/')
            cut_img_name = '{}_{}'.format(folder[0], img_prefix)
            for shape in data_info['labelme_info']['shapes']:
                num_obj += 1
                # 原始图片就有-与_,把-替换成下划线，
                # obj_file = img_prefix.replace('-', '').replace('_', '') + '_{:0>6d}'.format(num_obj) + img_suffix
                # 针对新需求-不替换下划线
                obj_file = cut_img_name.replace('.', '') + '_{:0>6d}'.format(num_obj) + img_suffix
                final_out_dir = os.path.join(gl_tmp_out_dir, shape['label'])
                # exist_ok=True，这样如果文件夹存在，会忽略创建文件夹
                os.makedirs(final_out_dir, exist_ok=True)
                # print(final_out_dir)
                crop_path = os.path.join(final_out_dir, obj_file)
                num_crop.append(crop_path)
                crop_obj = self.crop_rectangle(image, shape)
                if crop_obj.size == 0:
                    print("当前文件标注存在异常，路径如下所示:")
                    print(crop_path)
                # 默认像素小于10，就不进行截取，可以自动设置
                cv2.imencode(img_suffix, crop_obj)[1].tofile(crop_path)
                # if crop_obj.shape[0] * crop_obj.shape[1] > min_pixel:
                #     queue.put([crop_obj, crop_path, img_suffix])
                # # 多线程处理，抠图保存
                # while True:
                #     labelme_pool.apply_async(self.save, args=(queue,))
                #     if queue.qsize() > 50:
                #         continue
                #     else:
                #         break

    def _del_class(self, data_infos, name_classes, filter_flags):
        """
        根据类别进行筛选，根据类别属性进行筛选，根据形状进行筛选
        :param data_infos:
        :param name_classes:
        :param filter_flags:
        :return:
        """
        def shape(data_info):
            # print(data_info)
            # 满足条件的置空
            if data_info.get('labelme_info') is not None:
                name_classes_list = list()
                for shape_element in data_info.get('labelme_info').get('shapes'):
                    # 如果筛选的类别不是要筛选的类别，就追加到列表中然后删除。
                    if shape_element['label'] not in name_classes:
                        name_classes_list.append(shape_element)
                    if filter_flags is not None:
                        # 筛选类别的属性，是只筛选打勾的，并且属于筛选范围的
                        for flag in list(shape_element['flags']):  # 把字典进行循环，取键的值
                            if shape_element['flags'][flag]:  # 通过字典的键获取字典的值
                                if flag in filter_flags:  # 判断键的值是否在输入的列表中
                                    pass
                                else:
                                    del shape_element['flags'][flag]
                            else:
                                del shape_element['flags'][flag]
                for i in name_classes_list:
                    data_info.get('labelme_info').get('shapes').remove(i)
                # 针对按类别筛选后变成背景类的过滤。如果要保存背景类，筛选后变成背景类的数据没有保存。
                if data_info['labelme_info'].get('shapes').__len__() == 0 and data_info['background'] is False:
                    data_info['background'] = True
                if data_info['background'] and self.filter_empty is True:
                    return
                if data_info['background'] and self.filter_empty is False:
                    return data_info
                else:
                    return data_info

            if self.filter_empty is False and data_info.get('labelme_info') is None:
                return data_info

        # 没有这一步，过滤后等于没有过滤
        self.data_infos = list(filter(shape, data_infos))

    def _del_type(self, data_info, shapes_type):
        """
        shapes_type=['rectangle']
        根据标注形状进行筛选，比如rectangle(长方形)、circle(圆)、polygon(多边形)、line(线)
        :param type_shapes:
        """
        shapes_type = [shapes_type] if isinstance(shapes_type, str) else shapes_type
        for shape in data_info['labelme_info']['shapes']:
            if shape is None:
                if shape['shape_type'] not in shapes_type:
                    shape.clear()

    # 保存，传入保存路径，类别。客户想保存才保存
    def save_labelme(self, out_dir='./out_dir', replaces={}):
        """
        根据类别保存labelme。coco转labelme需要现在内存中与datainfos关联上，然后用该方法存储到磁盘上。
        :param out_dir:
        """
        if out_dir == '' or out_dir is None:
            print('传入的save_path={} 为空'.format(out_dir))
            raise ValueError
        if out_dir is not None and out_dir != '':
            os.makedirs(out_dir, exist_ok=True)
        print('类别保存处理进度:')
        global modify_labelme_dir, archive_json_path, archive_image_path
        for data_info in tqdm(self.data_infos):
            # 批量处理多文件夹数据集，把旧路径替换成自定义路径
            for old, new in replaces.items():
                replace_image_path = data_info['image_dir'].replace(old, new)
                replace_json_path = data_info['labelme_dir'].replace(old, new)
                # 3. 去掉开头的 斜杠
                image_slash = replace_image_path.strip('\\/')
                json_slash = replace_json_path.strip('\\/')
                archive_image_path = os.path.join(out_dir, image_slash)
                archive_json_path = os.path.join(out_dir, json_slash)
            labelme_dir = os.path.split(data_info['labelme_dir'])[-1]
            image_dir = os.path.split(data_info['image_dir'])[-1]
            # 针对李世娇，把00.labelme修改成01.labelme后无法查看问题，临时添加
            if '00.labelme' in data_info['labelme_dir']:
                archive_json_path = archive_json_path.replace(labelme_dir, '01.labelme')
            os.makedirs(archive_json_path, exist_ok=True)
            os.makedirs(archive_image_path, exist_ok=True)
            if data_info['image_file'] is not None:
                image_path = os.path.join(data_info['image_dir'], data_info['image_file'])
                try:
                    shutil.copy(image_path, archive_image_path)
                except Exception as e:
                    continue
                if data_info['labelme_file'] is not None:
                    save_json_path = os.path.join(archive_json_path, data_info['labelme_file'])
                    with open(save_json_path, "w", encoding='UTF-8') as labelme_fp:  # 以写入模式打开这个文件
                        json.dump(data_info['labelme_info'], labelme_fp, indent=4, cls=Encoder)  # 从新写入这个文件，把之前的覆盖掉（保存）

    def visualization(self, output_dir, replaces={}):
        """
        可视化保存图片方法实现
        :param output_dir:
        :param replaces:
        """
        global left_top, right_bottom, archive_image_path
        # os.makedirs(output_dir, exist_ok=True)
        for data_info in self.data_infos:
            image = os.path.join(data_info['image_dir'], data_info['image_file'])
            # output_image = os.path.join(output_dir, data_info['image_file'])
            img = cv2.imread(image)
            for old, new in replaces.items():
                replace_image_path = data_info['image_dir'].replace(old, new)
                # replace_json_path = data_info['labelme_dir'].replace(old, new)
                # 3. 去掉开头的 斜杠
                image_slash = replace_image_path.strip('\\/')
                # json_slash = replace_json_path.strip('\\/')
                archive_image_path = os.path.join(output_dir, image_slash)
                os.makedirs(archive_image_path, exist_ok=True)
                # archive_json_path = os.path.join(output_dir, json_slash)
            output_image = os.path.join(archive_image_path, data_info['image_file'])

            if data_info['labelme_info'] is not None:
                for shape in data_info['labelme_info']['shapes']:
                    # 左上角坐标点
                    left_top = (list(map(int, shape['points'][0])))
                    # 右下角坐标点
                    right_bottom = (list(map(int, shape['points'][1])))
                    # (0, 255, 255) => rgb 颜色,3 => 粗细程度,img => 图片数据,
                    cv2.rectangle(img, left_top, right_bottom, (0, 255, 255), 1)
                    # 保存图片
                    cv2.imwrite(output_image, img)

    def rename(self, rename):
        """
        重命名标签类别
        :param rename:
        """
        for data_info in self.data_infos:
            if data_info['labelme_info'] is not None:
                for shape in data_info['labelme_info']['shapes']:
                    # if shape['label'] == 'perosn':
                    #     print(shape['label'])
                    # 待追加功能：有标签错误，停止并等待用户输入正确的标签参数，然后继续执行。
                    if shape['label'] in rename.get('name_classes'):  # 修改标签类别名称
                        shape['label'] = rename.get('name_classes').get(shape['label'])
                    try:
                        for rename_key in rename.get('flags').keys():  # 修改标签类别属性名称
                            if rename_key in list(shape['flags'].keys()):
                                shape['flags'][rename.get('flags')[rename_key]] = shape['flags'].pop(rename_key)
                    except Exception as e:
                        # print(e)
                        continue

    def __add__(self, other):
        """
        类别筛选合并操作方法
        :param other:
        :return:
        """
        for index, info in enumerate(other.data_infos):
            # 找出info中的image_file，并把self.data_infos集合传入find(),用于查询other.data_infos中的元素是否在self.data_infos，不在就把other.data_infos元素追加到self.data_infos
            self.find(info['image_file'], self.data_infos)
            # 打印相等与不相等的索引下标
            # print(self.find(info['image_file'], self.data_infos))
            if self.find(info['image_file'], self.data_infos) is None:
                # 如果两个对象中的元素相等就labelme相加，不等的元素直接追加后保存
                self.data_infos.append(info)
                # 挑选不同的labelme元素进行追加
                self.different.append(info)
            if self.data_infos[self.find(info['image_file'], self.data_infos)].get('labelme_info') is None:
                continue
            # 针对需要追加的数据，如果没有shapes就不追加，直接跳过
            if info.get('labelme_info') is None:
                continue
            else:
                # print(self.data_infos[self.find(info['image_file'], self.data_infos)].get('labelme_info').get('shapes'))
                # print(info.get('labelme_info').get('shapes'))
                # print()
                self.data_infos[self.find(info['image_file'], self.data_infos)].get('labelme_info').get(
                    'shapes').extend(info.get('labelme_info').get('shapes'))
        return self

    # @update_property
    def __call__(self, filter_empty, only_empty=False, *args, **kwargs):
        """
        类别筛选功能实现。一个类实例也可以变成一个可调用对象，只需要实现一个特殊方法__call__()
        :param filter_empty: 默认False，保留背景类。设置为True，不保留背景类。
        :param only_empty: 默认False，不保留背景类。设置为True，只筛选背景类。
        :param args: 传入参数可为，数字、字符串
        :param kwargs: 传入参数可为，列表、元组、集合、字典。当前传入列表，参数有name_classes（类别）、shapes_type（形状）
        :return:
        """
        # print(kwargs.get('name_classes'))
        # print(kwargs.get('filter_flags'))
        # print(only_empty)
        global name_classes, shapes_type
        self.self_bak.filter_empty = filter_empty
        self.self_bak.only_empty = only_empty
        # 如果filter_empty和only_empty都为真，则报错
        if filter_empty and only_empty:
            assert not filter_empty, '即不需要背景类，同时又只保留背景类条件冲突，请核对业务需求重新传入参数{}'.format(filter_empty)
        # 只留背景类，把不是背景类的删除掉。
        if only_empty:
            def data_info_only_empty(data_info):
                # 如果不是背景类就剔除
                if not data_info['background']:
                    return
                return data_info

            if self.self_bak.only_empty:
                # print(self.self_bak.data_infos)
                self.self_bak.data_infos = list(filter(data_info_only_empty, self.self_bak.data_infos))
                self.self_bak.__update_property__()
                return self.self_bak
        else:
            # 先判断筛选条件是否合法，不合法终止运行。优先判断传入的类型是否为list
            if kwargs.get('name_classes'):
                name_classes = kwargs.get('name_classes')
                # 不是列表赋值成列表，传入的类别是否存在，
                if isinstance(name_classes, str):
                    name_classes = [name_classes]
                if not set(name_classes).issubset(set(self.name_classes)):
                    warnings.warn(
                        '传入的name_classes={} 不是self.name_classes={}的子集'.format(name_classes, self.name_classes))
            if kwargs.get('shapes_type'):
                shapes_type = kwargs.get('shapes_type')
                if isinstance(shapes_type, str):
                    shapes_type = [shapes_type]
                if not set(shapes_type).issubset(set(self.self_bak.shape_type)):
                    warnings.warn(
                        '传入的type_shapes={} 不是self.shape_type={}的子集'.format(shapes_type, self.self_bak.shape_type))
            if kwargs.get('filter_flags'):
                filter_flags = kwargs.get('filter_flags')
                if isinstance(filter_flags, str):
                    filter_flags = dict(filter_flags)
                if not set(filter_flags).issubset(set(self.flags)):
                    warnings.warn('filter_flags={} 不是self.flags={}的子集'.format(filter_flags, self.flags))

            def data_info_filter(data_info):
                if data_info['background']:
                    return
                return data_info

            if self.self_bak.filter_empty:
                self.self_bak.data_infos = list(filter(data_info_filter, self.self_bak.data_infos))
            if kwargs.get('name_classes'):
                # 筛选过程中只保留当前操作类别，其余不需要的类别不留
                self.self_bak._del_class(self.self_bak.data_infos, name_classes, filter_flags=None)
                self.self_bak.__update_property__()
                return self.self_bak

        # if kwargs.get('shapes_type'):
        # 该方法没有实现
        # self._del_type(self.data_infos, shapes_type)

    def self2labelme(self):
        # 子类没有实现就报错
        raise NotImplementedError

    def data_info_print(self):
        for dataset in self:
            print('Labelme 数据集图像路径:%s' % dataset.images_dir,
                  'Labelme 数据集注释路径:%s' % dataset.labelme_dir)
            print(dataset)
