from mtutils import DMDet
from mtutils import DMMC
from mtutils import DMML
from mtutils import MultiLabelEvaluator
from mtutils import DetectionEvaluator
from mtutils import MultiClassEvaluator


if __name__ == '__main__':

    # gt_info = DMDet.from_json('assets/gt.json')
    # pd_info = DMDet.from_json('assets/detection.json')
    # gt_info = DMDet.from_json('assets/gt-prediction/gt.json')
    # pd_info = DMDet.from_json('assets/gt-prediction/pipeline-results.json')
    gt_info = DMDet.from_json('assets/gt-pred/gt.json')
    pd_info = DMDet.from_json('assets/gt-pred/pipeline-results.json')

    gt_info = gt_info.to_ml()
    pd_info = pd_info.to_ml()

    # gt_info = gt_info.to_mc()
    # pd_info = pd_info.to_mc()

    gt_info.set_class(['NG'])
    pd_info.set_class(['NG'])

    evaluator = MultiLabelEvaluator(data_gt=gt_info, data_pred=pd_info)

    evaluator.set_threshold('manual', [0.5])
    print(evaluator.get_confusion_matrix())
    evaluator.dump_failure_case(r'Y:\raw\adc', target_dir='tmp')
    
    pass