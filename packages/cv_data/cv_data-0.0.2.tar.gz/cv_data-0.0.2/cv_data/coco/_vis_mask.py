from boxx import *
from boxx import np, os, npa, dicto, impt


import pycocotools.mask as mask_util

import cv2
import numpy as np
import matplotlib

# matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

plt.rcParams["pdf.fonttype"] = 42  # For editing in Adobe Illustrator


_GRAY = (218, 227, 218)
_GREEN = (18, 127, 15)
_WHITE = (255, 255, 255)


def colormap(rgb=False):
    color_list = np.array(
        [
            0.000,
            0.447,
            0.741,
            0.850,
            0.325,
            0.098,
            0.929,
            0.694,
            0.125,
            0.494,
            0.184,
            0.556,
            0.466,
            0.674,
            0.188,
            0.301,
            0.745,
            0.933,
            0.635,
            0.078,
            0.184,
            0.300,
            0.300,
            0.300,
            0.600,
            0.600,
            0.600,
            1.000,
            0.000,
            0.000,
            1.000,
            0.500,
            0.000,
            0.749,
            0.749,
            0.000,
            0.000,
            1.000,
            0.000,
            0.000,
            0.000,
            1.000,
            0.667,
            0.000,
            1.000,
            0.333,
            0.333,
            0.000,
            0.333,
            0.667,
            0.000,
            0.333,
            1.000,
            0.000,
            0.667,
            0.333,
            0.000,
            0.667,
            0.667,
            0.000,
            0.667,
            1.000,
            0.000,
            1.000,
            0.333,
            0.000,
            1.000,
            0.667,
            0.000,
            1.000,
            1.000,
            0.000,
            0.000,
            0.333,
            0.500,
            0.000,
            0.667,
            0.500,
            0.000,
            1.000,
            0.500,
            0.333,
            0.000,
            0.500,
            0.333,
            0.333,
            0.500,
            0.333,
            0.667,
            0.500,
            0.333,
            1.000,
            0.500,
            0.667,
            0.000,
            0.500,
            0.667,
            0.333,
            0.500,
            0.667,
            0.667,
            0.500,
            0.667,
            1.000,
            0.500,
            1.000,
            0.000,
            0.500,
            1.000,
            0.333,
            0.500,
            1.000,
            0.667,
            0.500,
            1.000,
            1.000,
            0.500,
            0.000,
            0.333,
            1.000,
            0.000,
            0.667,
            1.000,
            0.000,
            1.000,
            1.000,
            0.333,
            0.000,
            1.000,
            0.333,
            0.333,
            1.000,
            0.333,
            0.667,
            1.000,
            0.333,
            1.000,
            1.000,
            0.667,
            0.000,
            1.000,
            0.667,
            0.333,
            1.000,
            0.667,
            0.667,
            1.000,
            0.667,
            1.000,
            1.000,
            1.000,
            0.000,
            1.000,
            1.000,
            0.333,
            1.000,
            1.000,
            0.667,
            1.000,
            0.167,
            0.000,
            0.000,
            0.333,
            0.000,
            0.000,
            0.500,
            0.000,
            0.000,
            0.667,
            0.000,
            0.000,
            0.833,
            0.000,
            0.000,
            1.000,
            0.000,
            0.000,
            0.000,
            0.167,
            0.000,
            0.000,
            0.333,
            0.000,
            0.000,
            0.500,
            0.000,
            0.000,
            0.667,
            0.000,
            0.000,
            0.833,
            0.000,
            0.000,
            1.000,
            0.000,
            0.000,
            0.000,
            0.167,
            0.000,
            0.000,
            0.333,
            0.000,
            0.000,
            0.500,
            0.000,
            0.000,
            0.667,
            0.000,
            0.000,
            0.833,
            0.000,
            0.000,
            1.000,
            0.000,
            0.000,
            0.000,
            0.143,
            0.143,
            0.143,
            0.286,
            0.286,
            0.286,
            0.429,
            0.429,
            0.429,
            0.571,
            0.571,
            0.571,
            0.714,
            0.714,
            0.714,
            0.857,
            0.857,
            0.857,
            1.000,
            1.000,
            1.000,
        ]
    ).astype(np.float32)
    color_list = color_list.reshape((-1, 3)) * 255
    if not rgb:
        color_list = color_list[:, ::-1]
    return color_list


def convert_from_cls_format(cls_boxes, cls_segms, cls_keyps):
    """Convert from the class boxes/segms/keyps format generated by the testing
    code.
    """
    box_list = [b for b in cls_boxes if len(b) > 0]
    if len(box_list) > 0:
        boxes = np.concatenate(box_list)
    else:
        boxes = None
    if cls_segms is not None:
        segms = [s for slist in cls_segms for s in slist]
    else:
        segms = None
    if cls_keyps is not None:
        keyps = [k for klist in cls_keyps for k in klist]
    else:
        keyps = None
    classes = []
    for j in range(len(cls_boxes)):
        classes += [j] * len(cls_boxes[j])
    return boxes, segms, keyps, classes


def vis_bbox_opencv(img, bbox, thick=1):
    """Visualizes a bounding box."""
    (x0, y0, w, h) = bbox
    x1, y1 = int(x0 + w), int(y0 + h)
    x0, y0 = int(x0), int(y0)
    cv2.rectangle(img, (x0, y0), (x1, y1), _GREEN, thickness=thick)
    return img


def get_class_string(class_index, score, dataset):
    class_text = (
        dataset.classes[class_index]
        if dataset is not None
        else "id{:d}".format(class_index)
    )
    return class_text + " {:0.2f}".format(score).lstrip("0")


def iscn(char):
    """
    Does a char is chinese? 
    """
    if "\u4e00" <= char <= "\u9fff":
        return True
    return False


def pltcn(s):
    l = []
    for c in s:
        l.append(c)
        if iscn(c):
            l.append(" ")
    return "".join(l)


def vis_one_image(
    im,
    im_name,
    output_dir,
    boxes,
    segms=None,
    keypoints=None,
    thresh=0.9,
    kp_thresh=2,
    dpi=200,
    box_alpha=0.0,
    dataset=None,
    show_class=False,
    ext="pdf",
    pltshow=False,
):
    """Visual debugging of detections."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if isinstance(boxes, list):
        boxes, segms, keypoints, classes = convert_from_cls_format(
            boxes, segms, keypoints
        )

    if boxes is None or boxes.shape[0] == 0 or max(boxes[:, 4]) < thresh:
        return

    if segms is not None:
        masks = mask_util.decode(segms)

    color_list = colormap(rgb=True) / 255

    fig = plt.figure(frameon=False)
    fig.set_size_inches(im.shape[1] / dpi, im.shape[0] / dpi)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.axis("off")
    fig.add_axes(ax)
    ax.imshow(im)

    # Display in largest to smallest order to reduce occlusion
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    sorted_inds = np.argsort(-areas)

    mask_color_id = 0
    for i in sorted_inds:
        bbox = boxes[i, :4]
        score = boxes[i, -1]
        if score < thresh:
            continue

        # show box (off by default, box_alpha=0.0)
        ax.add_patch(
            plt.Rectangle(
                (bbox[0], bbox[1]),
                bbox[2] - bbox[0],
                bbox[3] - bbox[1],
                fill=False,
                edgecolor="g",
                linewidth=0.5,
                alpha=box_alpha,
            )
        )

        if show_class:
            ax.text(
                bbox[0],
                bbox[1] - 2,
                pltcn(get_class_string(classes[i], score, dataset)),
                fontsize=12,
                family="serif",
                bbox=dict(facecolor="g", alpha=0.2, pad=0, edgecolor="none"),
                color="white",
            )

        # show mask
        if segms is not None and len(segms) > i:
            img = np.ones(im.shape)
            color_mask = color_list[mask_color_id % len(color_list), 0:3]
            mask_color_id += 1

            w_ratio = 0.4
            for c in range(3):
                color_mask[c] = color_mask[c] * (1 - w_ratio) + w_ratio
            for c in range(3):
                img[:, :, c] = color_mask[c]
            e = masks[:, :, i]

            contour, hier = cv2.findContours(
                e.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE
            )[-2:]
            for c in contour:
                polygon = Polygon(
                    c.reshape((-1, 2)),
                    fill=True,
                    facecolor=color_mask,
                    edgecolor="w",
                    linewidth=1.2,
                    alpha=0.5,
                )
                ax.add_patch(polygon)

        # show keypoints
        if keypoints is not None and len(keypoints) > i:
            dataset_keypoints, _ = keypoint_utils.get_keypoints()
            kp_lines = kp_connections(dataset_keypoints)
            cmap = plt.get_cmap("rainbow")
            colors = [cmap(i) for i in np.linspace(0, 1, len(kp_lines) + 2)]

            kps = keypoints[i]
            plt.autoscale(False)
            for l in range(len(kp_lines)):
                i1 = kp_lines[l][0]
                i2 = kp_lines[l][1]
                if kps[2, i1] > kp_thresh and kps[2, i2] > kp_thresh:
                    x = [kps[0, i1], kps[0, i2]]
                    y = [kps[1, i1], kps[1, i2]]
                    line = ax.plot(x, y)
                    plt.setp(line, color=colors[l], linewidth=1.0, alpha=0.7)
                if kps[2, i1] > kp_thresh:
                    ax.plot(
                        kps[0, i1],
                        kps[1, i1],
                        ".",
                        color=colors[l],
                        markersize=3.0,
                        alpha=0.7,
                    )
                if kps[2, i2] > kp_thresh:
                    ax.plot(
                        kps[0, i2],
                        kps[1, i2],
                        ".",
                        color=colors[l],
                        markersize=3.0,
                        alpha=0.7,
                    )

            # add mid shoulder / mid hip for better visualization
            mid_shoulder = (
                kps[:2, dataset_keypoints.index("right_shoulder")]
                + kps[:2, dataset_keypoints.index("left_shoulder")]
            ) / 2.0
            sc_mid_shoulder = np.minimum(
                kps[2, dataset_keypoints.index("right_shoulder")],
                kps[2, dataset_keypoints.index("left_shoulder")],
            )
            mid_hip = (
                kps[:2, dataset_keypoints.index("right_hip")]
                + kps[:2, dataset_keypoints.index("left_hip")]
            ) / 2.0
            sc_mid_hip = np.minimum(
                kps[2, dataset_keypoints.index("right_hip")],
                kps[2, dataset_keypoints.index("left_hip")],
            )
            if (
                sc_mid_shoulder > kp_thresh
                and kps[2, dataset_keypoints.index("nose")] > kp_thresh
            ):
                x = [mid_shoulder[0], kps[0, dataset_keypoints.index("nose")]]
                y = [mid_shoulder[1], kps[1, dataset_keypoints.index("nose")]]
                line = ax.plot(x, y)
                plt.setp(line, color=colors[len(kp_lines)], linewidth=1.0, alpha=0.7)
            if sc_mid_shoulder > kp_thresh and sc_mid_hip > kp_thresh:
                x = [mid_shoulder[0], mid_hip[0]]
                y = [mid_shoulder[1], mid_hip[1]]
                line = ax.plot(x, y)
                plt.setp(
                    line, color=colors[len(kp_lines) + 1], linewidth=1.0, alpha=0.7
                )

        output_name = os.path.basename(im_name) + "." + ext
    fig.savefig(os.path.join(output_dir, "{}".format(output_name)), dpi=dpi)
    if pltshow:
        plt.show()
    plt.close("all")


from PIL import Image, ImageDraw


def poly2mask(bg, polys, fill=255):
    bg = Image.fromarray(bg)
    for poly in polys:
        if len(poly) >= 8:
            ImageDraw.Draw(bg).polygon(
                list(zip(poly[::2], poly[1::2])), outline=fill, fill=fill
            )
    bg = np.array(bg)
    return bg


def mask2rle(mask):
    import pycocotools.mask as mask_util

    mask = mask.astype(np.uint8)
    # Get RLE encoding used by the COCO evaluation API
    rle = mask_util.encode(np.array(mask[:, :, np.newaxis], order="F"))[0]
    # For dumping to json, need to decode the byte string.
    # https://github.com/cocodataset/cocoapi/issues/70
    rle["counts"] = rle["counts"].decode("ascii")
    return rle


def visMask(
    rgb,
    gts,
    name="tmp",
    outputDir=None,
    id2cat=None,
    box_alpha=0.8,
    show_class=True,
    thresh=0.1,
    show_mask=True,
    pltshow=False,
    ext="jpg",
):
    dataset = dicto(classes=id2cat)
    if outputDir is None:
        outputDir = "/tmp/visCanvas"
    if id2cat is None:
        dataset = dicto(classes={i: "%d-class" % i for i in range(1111)})
    #    classn = len(dataset.classes)
    maxCatId = max(dataset.classes.keys()) + 1
    cls_segms = [[] for _ in range(maxCatId)]
    cls_boxes = [np.zeros((0, 5), np.float32) for _ in range(maxCatId)]

    # cls_segms = None
    # cls_boxes = [np.zeros((0,5), np.float32) for _ in range(classn)]
    for gt in gts:
        c = gt.clas
        if show_mask:
            rle = mask2rle(gt.mask)
            cls_segms[c].append(rle)
        lurd = gt.get("lurd")
        if not lurd:
            lurd = gt.urdl[-1:] + gt.urdl[:3]
        boxarr = npa([list(lurd) + [1]])
        #        import boxx.g
        cls_boxes[c] = np.append(cls_boxes[c], boxarr, 0)

    cls_keyps = None
    if not show_mask:
        cls_segms = None
    #    g()

    vis_one_image(
        rgb,  # BGR -> RGB for visualization
        name,
        outputDir,
        cls_boxes,
        cls_segms,
        cls_keyps,
        dataset=dataset,
        box_alpha=box_alpha,
        show_class=True,
        thresh=thresh,
        kp_thresh=2,
        pltshow=pltshow,
        ext=ext,
    )
