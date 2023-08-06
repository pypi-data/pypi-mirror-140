from tqdm import tqdm

from sklearn.metrics import confusion_matrix
from pathlib import Path
from ....utils_vvd import encode_path
from ....utils_vvd import cv_rgb_imwrite
from ....utils_vvd import cv_rgb_imread
from .base import EvaluatorBase
import pandas as pd


class ClassificationMultiClassEvaluator(EvaluatorBase):
    TYPE = 'MultiClass'
    def _data_check(self, gt_data, pd_data):
        assert gt_data.class_dict == pd_data.class_dict, f"differect class_dict between {gt_data.class_dict} and {pd_data.class_dict}"
        pass

    def _get_result_dict(self, dm):
        result_dict = dict()
        for rec in dm:
            class_name = self.am.get_classname(rec)
            result_dict[rec['info']['uuid']] = class_name
        return result_dict

    def _get_gt_result_dict(self, dm_gt):
        return self._get_result_dict(dm_gt)

    def _get_pred_result_dict(self, dm_pred):
        return self._get_result_dict(dm_pred)

    def get_confusion_matrix(self):
        y_true = self.gt_data_list
        y_pred = self.pred_data_list
        cm = confusion_matrix(y_true=y_true, y_pred=y_pred, labels=self.classnames)
        cm_pd = pd.DataFrame(cm, index=self.classnames, columns=self.classnames)
        return cm_pd
    
    def dump_failure_case(self, data_root, target_dir):
        target_dir = Path(target_dir)
        for y_true, y_pred, data_path in tqdm(zip(self.gt_data_list, self.pred_data_list, self.data_path_list), total=len(self.gt_data_list)):
            if y_true != y_pred:
                ori_img_path = Path(data_root) / data_path
                if not ori_img_path.exists():
                    print(f"Ori image path {ori_img_path} not found.")
                    continue
                else:
                    try:
                        image = cv_rgb_imread(ori_img_path)
                    except Exception as e:
                        print(f"image load failed! {ori_img_path}")
                        print(f"error message: {e}")
                        continue
                gt_label = self.classnames[y_true]
                pred_label = self.classnames[y_pred]
                save_path = target_dir / gt_label / pred_label / encode_path(ori_img_path)
                cv_rgb_imwrite(image, save_path)


MultiClassEvaluator = ClassificationMultiClassEvaluator
