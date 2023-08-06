import boxx
from boxx import *
from boxx import pathjoin, imread, dicto, makedirs, filename
from boxx import glob, loadCoco, impt, np
from pycocotools import mask as masktool
import tqdm

with inpkg():
    from ._vis_mask import visMask
    from .utils import coco_seg_to_mask

__doc__ = """
example:
    
python -m cv_data.coco.vis
    [--jsp] s3://dataset/coco/instances_train2017.json
    [--num 100]
    [--dst /tmp/cv_data-coco-vis]
    [--gap 10]
    [--imgdir s3://dataset/coco/train2017]

- support oss
- support import as func
- support cli
"""

test_example = boxx.relfile(
    "../../../cv_data_test_data/tiny_coco/instances_train2017.json"
)
default_jsp = (
    test_example if "/cv_data" in os.path.abspath(".") else "*instances_*.json"
)

default = dict(
    jsp=default_jsp,
    dst="/tmp/cv_data-coco-vis",
    num=0,  # how many images to be vis each image dir
    gap=1,
)

print(sys.argv)
fix_arg = dict()

_, args = boxx.getArgvDic()

if len(args) == 0:
    print(__doc__)

[args.setdefault(k, v) for k, v in fix_arg.items()]


def vis_coco(args):
    [args.setdefault(k, default[k]) for k in default]
    boxx.tree - args
    for jsp in boxx.glob(args["jsp"]):
        _imgdir = jsp.replace("annotations", "images").replace("instances_", "")[:-5]
        imgdir = args.get("imgdir", _imgdir)
        print("imgdir:", imgdir)
        with boxx.timeit(loadCoco):
            cocoDic, _imgdf, anndf, catdf = loadCoco(jsp)

        imgdf = _imgdf[
            _imgdf.file_name.apply(
                lambda fname: os.path.isfile(pathjoin(imgdir, fname))
            )
        ]
        assert len(imgdf), "Not found any image both in coco json and " + imgdir
        if len(imgdf) != len(_imgdf):
            boxx.pred(
                f"Image files are a small sample of coco json, {len(imgdf)}/{len(_imgdf)}"
            )

        if args["num"]:
            args["gap"] = max(len(imgdf) // args["num"], args["gap"])

        inds = list(range(len(imgdf)))[:: args["gap"]]
        for ind in tqdm.tqdm(inds):
            # if ind % args["gap"]:
            #     continue
            row = imgdf.iloc[ind]
            imgp = pathjoin(imgdir, row.file_name)
            img = imread(imgp)
            annds = anndf[anndf.image_id == row.id]
            if "area" in annds:
                annds = annds.sort_values("area", ascending=False)

            bbox2Lurd = lambda bbox: bbox[:2] + [bbox[0] + bbox[2], bbox[1] + bbox[3]]
            gts = [
                dicto(
                    lurd=bbox2Lurd(annd.bbox),
                    clas=annd.category_id,
                    mask=coco_seg_to_mask(annd.segmentation, [row.height, row.width]),
                )
                for i, annd in annds.iterrows()
            ]
            id2cat = dict(catdf.set_index("id").name)

            visMask(
                img,
                gts,
                name=filename(row.file_name.replace("/", "-")),
                outputDir=args["dst"] or None,
                id2cat=id2cat,
                pltshow=not args["dst"],
            )

            if args["num"] and boxx.increase() >= args["num"] - 1:
                break
    print("Saving coco vis to:", args["dst"])


if __name__ == "__main__":
    vis_coco(args)
