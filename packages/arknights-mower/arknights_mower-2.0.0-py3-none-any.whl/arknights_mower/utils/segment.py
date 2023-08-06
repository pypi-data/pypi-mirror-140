from __future__ import annotations

import cv2
import traceback
import imagehash
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont

from . import typealias as tp
from .image import rgb2gray, thres0
from .log import logger
from .recognize import RecognizeError
from .. import __rootdir__
from ..data.agent import agent_list
from ..data.ocr import ocr_error
from ..ocr import ocrhandle


class FloodCheckFailed(Exception):
    pass


def get_poly(x1: int, x2: int, y1: int, y2: int) -> tp.Rectangle:
    x1, x2 = int(x1), int(x2)
    y1, y2 = int(y1), int(y2)
    return np.array([[x1, y1], [x1, y2], [x2, y2], [x2, y1]])


def credit(img: tp.Image, draw: bool = False) -> list[tp.Scope]:
    """
    信用交易所特供的图像分割算法
    """
    try:
        height, width, _ = img.shape

        left, right = 0, width
        while np.max(img[:, right-1]) < 100:
            right -= 1
        while np.max(img[:, left]) < 100:
            left += 1

        def average(i: int) -> int:
            num, sum = 0, 0
            for j in range(left, right):
                if img[i, j, 0] == img[i, j, 1] and img[i, j, 1] == img[i, j, 2]:
                    num += 1
                    sum += img[i, j, 0]
            return sum // num

        def ptp(j: int) -> int:
            maxval = -999999
            minval = 999999
            for i in range(up_1, up_2):
                minval = min(minval, img[i, j, 0])
                maxval = max(maxval, img[i, j, 0])
            return maxval - minval

        up_1 = 0
        flag = False
        while not flag or average(up_1) >= 250:
            flag |= average(up_1) >= 250  # numpy.bool_
            up_1 += 1

        up_2 = up_1
        flag = False
        while not flag or average(up_2) < 220:
            flag |= average(up_2) < 220
            up_2 += 1

        down = height - 1
        while average(down) < 180:
            down -= 1

        right = width - 1
        while ptp(right) < 50:
            right -= 1

        left = 0
        while ptp(left) < 50:
            left += 1

        split_x = [left + (right - left) // 5 * i for i in range(0, 6)] 
        split_y = [up_1, (up_1 + down) // 2, down]

        ret = []
        for y1, y2 in zip(split_y[:-1], split_y[1:]):
            for x1, x2 in zip(split_x[:-1], split_x[1:]):
                ret.append(((x1, y1), (x2, y2)))

        if draw:
            for y1, y2 in zip(split_y[:-1], split_y[1:]):
                for x1, x2 in zip(split_x[:-1], split_x[1:]):
                    cv2.polylines(img, [get_poly(x1, x2, y1, y2)],
                                  True, 0, 10, cv2.LINE_AA)
            plt.imshow(img)
            plt.show()

        logger.debug(f'segment.credit: {ret}')
        return ret

    except Exception as e:
        logger.debug(traceback.format_exc())
        raise RecognizeError(e)


def recruit(img: tp.Image, draw: bool = False) -> list[tp.Scope]:
    """
    公招特供的图像分割算法
    """
    try:
        height, width, _ = img.shape
        left, right = width//2-100, width//2-50

        def adj_x(i: int) -> int:
            if i == 0:
                return 0
            sum = 0
            for j in range(left, right):
                for k in range(3):
                    sum += abs(int(img[i, j, k]) - int(img[i-1, j, k]))
            return sum // (right-left)

        def adj_y(j: int) -> int:
            if j == 0:
                return 0
            sum = 0
            for i in range(up_2, down_2):
                for k in range(3):
                    sum += abs(int(img[i, j, k]) - int(img[i, j-1, k]))
            return int(sum / (down_2-up_2))

        def average(i: int) -> int:
            sum = 0
            for j in range(left, right):
                sum += np.sum(img[i, j, :3])
            return sum // (right-left) // 3

        def minus(i: int) -> int:
            s = 0
            for j in range(left, right):
                s += int(img[i, j, 2]) - int(img[i, j, 0])
            return s // (right-left)

        up = 0
        while minus(up) > -100:
            up += 1
        while not (adj_x(up) > 80 and minus(up) > -10 and average(up) > 210):
            up += 1
        up_2, down_2 = up-90, up-40

        left = 0
        while np.max(img[:, left]) < 100:
            left += 1
        left += 1
        while adj_y(left) < 50:
            left += 1

        right = width - 1
        while np.max(img[:, right]) < 100:
            right -= 1
        while adj_y(right) < 50:
            right -= 1

        split_x = [left, (left + right) // 2, right]
        down = height - 1
        split_y = [up, (up + down) // 2, down]

        ret = []
        for y1, y2 in zip(split_y[:-1], split_y[1:]):
            for x1, x2 in zip(split_x[:-1], split_x[1:]):
                ret.append(((x1, y1), (x2, y2)))

        if draw:
            for y1, y2 in zip(split_y[:-1], split_y[1:]):
                for x1, x2 in zip(split_x[:-1], split_x[1:]):
                    cv2.polylines(img, [get_poly(x1, x2, y1, y2)],
                                  True, 0, 10, cv2.LINE_AA)
            plt.imshow(img)
            plt.show()

        logger.debug(f'segment.recruit: {ret}')
        return ret

    except Exception as e:
        logger.debug(traceback.format_exc())
        raise RecognizeError(e)


def base(img: tp.Image, central: tp.Scope, draw: bool = False) -> dict[str, tp.Rectangle]:
    """
    基建布局的图像分割算法
    """
    try:
        ret = {}

        x1, y1 = central[0]
        x2, y2 = central[1]
        alpha = (y2 - y1) / 160
        x1 -= 170 * alpha
        x2 += 182 * alpha
        y1 -= 67 * alpha
        y2 += 67 * alpha
        central = get_poly(x1, x2, y1, y2)
        ret['central'] = central

        for i in range(1, 5):
            y1 = y2 + 25 * alpha
            y2 = y1 + 134 * alpha
            if i & 1:
                dormitory = get_poly(x1, x2 - 158 * alpha, y1, y2)
            else:
                dormitory = get_poly(x1 + 158 * alpha, x2, y1, y2)
            ret[f'dormitory_{i}'] = dormitory

        x1, y1 = ret['dormitory_1'][0]
        x2, y2 = ret['dormitory_1'][2]

        x1 = x2 + 419 * alpha
        x2 = x1 + 297 * alpha
        factory = get_poly(x1, x2, y1, y2)
        ret[f'factory'] = factory

        y2 = y1 - 25 * alpha
        y1 = y2 - 134 * alpha
        meeting = get_poly(x1 - 158 * alpha, x2, y1, y2)
        ret[f'meeting'] = meeting

        y1 = y2 + 25 * alpha
        y2 = y1 + 134 * alpha
        y1 = y2 + 25 * alpha
        y2 = y1 + 134 * alpha
        contact = get_poly(x1, x2, y1, y2)
        ret[f'contact'] = contact

        y1 = y2 + 25 * alpha
        y2 = y1 + 134 * alpha
        train = get_poly(x1, x2, y1, y2)
        ret[f'train'] = train

        for floor in range(1, 4):
            x1, y1 = ret[f'dormitory_{floor}'][0]
            x2, y2 = ret[f'dormitory_{floor}'][2]
            x2 = x1 - 102 * alpha
            x1 = x2 - 295 * alpha
            if floor & 1 == 0:
                x2 = x1 - 24 * alpha
                x1 = x2 - 295 * alpha
            room = get_poly(x1, x2, y1, y2)
            ret[f'room_{floor}_3'] = room
            x2 = x1 - 24 * alpha
            x1 = x2 - 295 * alpha
            room = get_poly(x1, x2, y1, y2)
            ret[f'room_{floor}_2'] = room
            x2 = x1 - 24 * alpha
            x1 = x2 - 295 * alpha
            room = get_poly(x1, x2, y1, y2)
            ret[f'room_{floor}_1'] = room

        if draw:
            polys = list(ret.values())
            cv2.polylines(img, polys, True, (255, 0, 0), 10, cv2.LINE_AA)
            plt.imshow(img)
            plt.show()

        logger.debug(f'segment.base: {ret}')
        return ret

    except Exception as e:
        logger.debug(traceback.format_exc())
        raise RecognizeError(e)


def worker(img: tp.Image, draw: bool = False) -> tuple[list[tp.Rectangle], tp.Rectangle, bool]:
    """
    进驻总览的图像分割算法
    """
    try:
        height, width, _ = img.shape

        left, right = 0, width
        while np.max(img[:, right-1]) < 100:
            right -= 1
        while np.max(img[:, left]) < 100:
            left += 1

        x0 = right-1
        while np.average(img[:, x0, 1]) >= 100:
            x0 -= 1
        x0 -= 2

        seg = []
        remove_mode = False
        pre, st = int(img[0, x0, 1]), 0
        for y in range(1, height):
            remove_mode |= img[y, x0, 0] - img[y, x0, 1] > 40
            if np.ptp(img[y, x0]) <= 1 or int(img[y, x0, 0]) - int(img[y, x0, 1]) > 40:
                now = int(img[y, x0, 1])
                if abs(now - pre) > 20:
                    if now < pre and st == 0:
                        st = y
                    elif now > pre and st != 0:
                        seg.append((st, y))
                        st = 0
                pre = now
            elif st != 0:
                seg.append((st, y))
                st = 0
        # if st != 0:
        #     seg.append((st, height))
        logger.debug(f'segment.worker: seg {seg}')

        remove_button = get_poly(x0-10, x0, seg[0][0], seg[0][1])
        seg = seg[1:]

        for i in range(1, len(seg)):
            if seg[i][1] - seg[i][0] > 9:
                x1 = x0
                while img[seg[i][1]-3, x1-1, 2] < 100:
                    x1 -= 1
                break

        ret = []
        for i in range(len(seg)):
            if seg[i][1] - seg[i][0] > 9:
                ret.append(get_poly(x1, x0, seg[i][0], seg[i][1]))

        if draw:
            cv2.polylines(img, ret, True, (255, 0, 0), 10, cv2.LINE_AA)
            plt.imshow(img)
            plt.show()

        logger.debug(f'segment.worker: {[x.tolist() for x in ret]}')
        return ret, remove_button, remove_mode

    except Exception as e:
        logger.debug(traceback.format_exc())
        raise RecognizeError(e)


agent_ahash = None


def agent_ahash_init():
    global agent_ahash
    if agent_ahash is None:
        logger.debug('agent_ahash_init')
        agent_ahash = {}
        font = ImageFont.truetype(
            f'{__rootdir__}/fonts/SourceHanSansSC-Bold.otf', size=30, encoding='utf-8')
        for text in agent_list:
            dt = np.zeros((500, 500, 3), dtype=int)
            img = Image.fromarray(np.uint8(dt))
            ImageDraw.Draw(img).text((0, 0), text, (255, 255, 255), font=font)
            img = np.array(img)

            x0 = 0
            while (img[:, x0] == 0).all():
                x0 += 1
            x1 = img.shape[1]
            while (img[:, x1-1] == 0).all():
                x1 -= 1
            y0 = 0
            while (img[y0, x0:x1] == 0).all():
                y0 += 1
            y1 = img.shape[0]
            while (img[y1-1, x0:x1] == 0).all():
                y1 -= 1

            agent_ahash[text] = str(imagehash.average_hash(
                Image.fromarray(img[y0:y1, x0:x1]), 16))


def agent(im, draw=False):
    """
    干员总览的图像分割算法
    """
    try:
        h, w, _ = im.shape

        # gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        # gray = 255 - gray

        l, r = 0, w
        while np.max(im[:, r-1]) < 100:
            r -= 1
        while np.max(im[:, l]) < 100:
            l += 1

        x0 = l + 1
        while not (im[h-1, x0-1, 0] > im[h-1, x0, 0] + 10 and abs(int(im[h-1, x0, 0]) - int(im[h-1, x0+1, 0])) < 5):
            x0 += 1

        ocr = ocrhandle.predict(im[:, x0:r])

        segs = [(min(x[2][0][1], x[2][1][1]), max(x[2][2][1], x[2][3][1]))
                for x in ocr if x[1] in agent_list]
        while True:
            _a, _b = None, None
            for i in range(len(segs)):
                for j in range(len(segs)):
                    if i != j and (segs[i][0] <= segs[j][0] <= segs[i][1] or segs[i][0] <= segs[j][1] <= segs[i][1]):
                        _a, _b = segs[i], segs[j]
                        break
                if _b is not None:
                    break
            if _b is not None:
                segs.remove(_a)
                segs.remove(_b)
                segs.append((min(_a[0], _b[0]), max(_a[1], _b[1])))
            else:
                break
        segs = sorted(segs)
        for x in segs:
            if x[1] < h // 2:
                y0, y1 = x
            y2, y3 = x
        card_gap = y1 - y0
        logger.debug([y0, y1, y2, y3])

        x_set = set()
        for x in ocr:
            if x[1] in agent_list and (y0 <= x[2][0][1] <= y1 or y2 <= x[2][0][1] <= y3):
                x_set.add(x[2][1][0])
                x_set.add(x[2][2][0])
        x_set = sorted(x_set)
        logger.debug(x_set)
        x_set = [x_set[0]] + \
            [y for x, y in zip(x_set[:-1], x_set[1:]) if y - x > 80]
        gap = [y - x for x, y in zip(x_set[:-1], x_set[1:])]
        gap = [x for x in gap if x - np.min(gap) < 40]
        gap = int(np.average(gap))
        for x, y in zip(x_set[:-1], x_set[1:]):
            if y - x > 40:
                gap_num = round((y - x) / gap)
                for i in range(1, gap_num):
                    x_set.append(int(x + (y - x) / gap_num * i))
        while np.min(x_set) > 0:
            x_set.append(np.min(x_set) - gap)
        while np.max(x_set) < r - x0:
            x_set.append(np.max(x_set) + gap)
        x_set = sorted(x_set)
        logger.debug(x_set)

        ret = []
        for x1, x2 in zip(x_set[:-1], x_set[1:]):
            if 0 <= x1+card_gap and x0+x2+5 <= r:
                ret += [get_poly(x0+x1+card_gap, x0+x2+5, y0, y1),
                        get_poly(x0+x1+card_gap, x0+x2+5, y2, y3)]

        def poly_center(poly):
            return (np.average([x[0] for x in poly]), np.average([x[1] for x in poly]))

        def in_poly(poly, p):
            return poly[0, 0] <= p[0] <= poly[2, 0] and poly[0, 1] <= p[1] <= poly[2, 1]

        # if draw:
        #     cv2.polylines(im, ret, True, (255, 0, 0), 3, cv2.LINE_AA)
        #     plt.imshow(im)
        #     plt.show()

        def flood(img, dt):
            h, w = img.shape
            while True:
                pre_count = (dt > 0).sum()
                for x in range(1, w):
                    dt[:, x][(dt[:, x-1] > 0) & (img[:, x] > 0)] = 1
                for y in range(h-2, -1, -1):
                    dt[y][(dt[y+1] > 0) & (img[y] > 0)] = 1
                for x in range(w-2, -1, -1):
                    dt[:, x][(dt[:, x+1] > 0) & (img[:, x] > 0)] = 1
                for y in range(1, h):
                    dt[y][(dt[y-1] > 0) & (img[y] > 0)] = 1
                if pre_count == (dt > 0).sum():
                    break

        def ahash_recog(origin_img, scope):
            agent_ahash_init()
            origin_img = origin_img[scope[0, 1]:scope[2, 1], scope[0, 0]:scope[2, 0]]
            h, w = origin_img.shape[:2]
            thresh = 70
            while True:
                try:
                    img = rgb2gray(thres0(origin_img, thresh))
                    dt = np.zeros((h, w), dtype=np.uint8)
                    for y in range(h):
                        if img[y, w-1] != 0:
                            dt[y, w-1] = 1
                    flood(img, dt)
                    for y in range(h-1, h//2, -1):
                        count = 0
                        for x in range(w-1, -1, -1):
                            if dt[y, x] != 0:
                                count += 1
                            else:
                                break
                        if not (dt[y, :] > 0).all():
                            for x in range(w):
                                if dt[y, x] != 0:
                                    count += 1
                                else:
                                    break
                        if (dt[y] > 0).sum() != count:
                            logger.debug(f'{y}, {count}')
                            raise FloodCheckFailed

                    for y in range(h):
                        if img[y, 0] != 0:
                            dt[y, 0] = 1
                    for x in range(w):
                        if img[h-1, x] != 0:
                            dt[h-1, x] = 1
                        if img[0, x] != 0:
                            dt[0, x] = 1
                    flood(img, dt)
                    img[dt > 0] = 0
                    if (img > 0).sum() == 0:
                        raise FloodCheckFailed

                    x0, x1, y0, y1 = 0, w, 0, h
                    while True:
                        while (img[y0:y1, x0] == 0).all():
                            x0 += 1
                        while (img[y0:y1, x1-1] == 0).all():
                            x1 -= 1
                        while (img[y0, x0:x1] == 0).all():
                            y0 += 1
                        while (img[y1-1, x0:x1] == 0).all():
                            y1 -= 1
                        for x in range(x0, x1-10+1):
                            if (img[y0:y1, x:x+10] == 0).all():
                                x0 = x
                                break
                        if (img[y0:y1, x0] == 0).all():
                            continue
                        for y in range(y0, y1-10+1):
                            if (img[y:y+10, x0:x1] == 0).all():
                                y0 = y
                                break
                        if (img[y0, x0:x1] == 0).all():
                            continue
                        break

                    dt = np.zeros((y1-y0, x1-x0, 3), dtype=np.uint8)
                    dt[:, :, 0] = img[y0:y1, x0:x1]
                    dt[:, :, 1] = img[y0:y1, x0:x1]
                    dt[:, :, 2] = img[y0:y1, x0:x1]
                    ahash = str(imagehash.average_hash(Image.fromarray(dt), 16))
                    p = [(bin(int(ahash, 16) ^ int(agent_ahash[x], 16)).count('1'), x) for x in agent_ahash.keys()]
                    p = sorted(p)
                    logger.debug(p[:10])
                    if p[1][0] - p[0][0] < 10:
                        raise FloodCheckFailed
                    logger.debug(p[0][1])
                    return p[0][1]

                except FloodCheckFailed:
                    thresh += 5
                    logger.debug(f'add thresh to {thresh}')
                    if thresh > 100:
                        break
                    continue
            return None

        ret_succ = []
        ret_fail = []
        ret_agent = []
        for poly in ret:
            found_ocr, fx = None, 0
            for x in ocr:
                cx, cy = poly_center(x[2])
                if in_poly(poly, (cx+x0, cy)) and cx > fx:
                    fx = cx
                    found_ocr = x

            if found_ocr is not None:
                x = found_ocr
                if x[1] in agent_list:
                    ret_agent.append(x[1])
                    ret_succ.append(poly)
                    continue
                res = ocrhandle.predict(
                    thres0(im[poly[0, 1]-20:poly[2, 1]+20, poly[0, 0]-20:poly[2, 0]+20], 70))
                if len(res) > 0 and res[0][1] in agent_list:
                    x = res[0]
                    ret_agent.append(x[1])
                    ret_succ.append(poly)
                    continue
                res = ahash_recog(im, poly)
                if res is not None:
                    logger.warning(f'干员名称识别异常：{x[1]} 应为 {res}')
                    ocr_error[x[1]] = res
                    ret_agent.append(res)
                    ret_succ.append(poly)
                    continue
                logger.warning(
                    f'干员名称识别异常：{x[1]} 为不存在的数据，请报告至 https://github.com/Konano/arknights-mower/issues')
            else:
                res = ocrhandle.predict(
                    thres0(im[poly[0, 1]-20:poly[2, 1]+20, poly[0, 0]-20:poly[2, 0]+20], 70))
                if len(res) > 0 and res[0][1] in agent_list:
                    res = res[0][1]
                    ret_agent.append(res)
                    ret_succ.append(poly)
                    continue
                res = ahash_recog(im, poly)
                if res is not None:
                    ret_agent.append(res)
                    ret_succ.append(poly)
                    continue
                logger.warning(f'干员名称识别异常：区域 {poly}')
            ret_fail.append(poly)

        if draw and len(ret_fail):
            cv2.polylines(im, ret_fail, True, (255, 0, 0), 3, cv2.LINE_AA)
            plt.imshow(im)
            plt.show()

        logger.debug(f'segment.agent: {ret_agent}')
        logger.debug(f'segment.agent: {[x.tolist() for x in ret]}')
        return list(zip(ret_agent, ret_succ))

    except Exception as e:
        logger.debug(traceback.format_exc())
        raise RecognizeError(e)
