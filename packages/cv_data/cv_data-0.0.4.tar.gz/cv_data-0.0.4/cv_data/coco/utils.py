import boxx
from boxx import np, dicto, Vector, pathjoin, imread

import pycocotools.mask


def poly_to_mask(polys, hw=(1080, 1920)):
    """
    Reference:
        https://github.com/matterport/Mask_RCNN/blob/8bed8428a9698825de06ff7277fd5cff91aeb77f/samples/coco/coco.py#L282
    """
    rles = pycocotools.mask.frPyObjects(polys, hw[0], hw[1])
    rle = pycocotools.mask.merge(rles)
    return pycocotools.mask.decode(rle)


def coco_seg_to_mask(segmentation, hw=None):
    if isinstance(segmentation, dict):
        hw = segmentation["size"]
        counts = segmentation["counts"]
        if isinstance(counts, list):
            rle = pycocotools.mask.frPyObjects(segmentation, hw[0], hw[1])
        else:
            rle = segmentation
        return pycocotools.mask.decode(rle)
    else:
        if hw is None:
            hw = (1080, 1920)
        return poly_to_mask(segmentation, hw)


def mask2poly(
    mask,
    category_id=0,
    img_name=None,
    save_segmentation=True,
    shrank_stride=1,
    seg_type="rle",
    approx_poly_epsilon=1,
):

    ground_truth_binary_mask = np.uint8(mask)
    fortran_ground_truth_binary_mask = np.asfortranarray(ground_truth_binary_mask)
    encoded_ground_truth = pycocotools.mask.encode(fortran_ground_truth_binary_mask)
    ground_truth_area = pycocotools.mask.area(encoded_ground_truth)
    ground_truth_bounding_box = pycocotools.mask.toBbox(encoded_ground_truth)

    annotation = {
        "segmentation": [[1, 1, 1, 2, 2, 2]],
        "area": ground_truth_area.tolist(),
        "iscrowd": 0,
        "image_id": 0,
        "bbox": ground_truth_bounding_box.tolist(),
        "category_id": int(category_id),
        "id": 1,
        "img_name": img_name,
    }
    if save_segmentation:
        if seg_type == "rle":
            encoded_ground_truth["counts"] = encoded_ground_truth["counts"].decode(
                "ascii"
            )
            annotation["segmentation"] = encoded_ground_truth
        else:
            if seg_type == "cv2":
                import cv2

                contours, hierarchy = cv2.findContours(
                    (ground_truth_binary_mask).astype(np.uint8),
                    cv2.RETR_TREE,
                    cv2.CHAIN_APPROX_SIMPLE,
                )[-2:]
            elif seg_type == "skimage":
                # shrank the number of points to reduce the size of annotation
                import skimage.measure

                contours = skimage.measure.find_contours(ground_truth_binary_mask, 0.5)
            contours = [
                cv2.approxPolyDP(cnt, approx_poly_epsilon, True) for cnt in contours
            ]
            annotation["segmentation"] = []
            for contour in contours:
                contour = np.flip(contour, axis=1).round().astype(int)
                segmentation = contour.ravel().tolist()
                if shrank_stride > 1 and len(segmentation) > shrank_stride * 2 * 10:
                    segmentation = (
                        np.array(segmentation)
                        .reshape(-1, 2)[::shrank_stride]
                        .round()
                        .astype(int)
                        .ravel()
                        .tolist()
                    )
                # fix TypeError: Argument 'bb' has incorrect type (expected numpy.ndarray, got list)
                while len(segmentation) <= 4:
                    segmentation += segmentation[-2:]
                annotation["segmentation"].append(segmentation)

    return annotation
