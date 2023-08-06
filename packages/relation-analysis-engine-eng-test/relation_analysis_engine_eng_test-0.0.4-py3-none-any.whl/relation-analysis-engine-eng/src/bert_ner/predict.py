import logging

import torch
import torch.nn.functional as F
from torch.utils import data
from tqdm import tqdm
from transformers import BertTokenizer

from .data_set import NerProcessor, NERDataSet
from .model import CoNLLClassifier

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def get_process_field(root):
    process_field = []
    for child in root.iter("ProcessField"):
        for i in child:
            process_field.append(i.attrib.get("name"))
    return process_field

def eval(iter_data, model, args):
    logger.info("starting to evaluate")
    tags_vals = NerProcessor().get_labels()
    model = model.eval()
    eval_loss, eval_accuracy = 0, 0
    nb_eval_steps = 0
    predictions, true_labels = [], []
    for batch in tqdm(iter_data):
        batch = tuple(t.to(args.device) for t in batch)

        b_input_ids, b_labels, b_input_mask, b_token_type_ids, b_label_masks = batch
        
        with torch.no_grad():
            tmp_eval_loss, logits, reduced_labels = model(b_input_ids,
                                                          token_type_ids=b_token_type_ids,
                                                          attention_mask=b_input_mask,
                                                          labels=b_labels,
                                                          label_masks=b_label_masks)

        logits = torch.argmax(F.log_softmax(logits, dim=2), dim=2)
        logits = logits.detach().cpu().numpy()
        reduced_labels = reduced_labels.to('cpu').numpy()

        labels_to_append = []
        predictions_to_append = []

        for prediction, r_label in zip(logits, reduced_labels):
            preds = []
            labels = []
            for pred, lab in zip(prediction, r_label):
                if lab.item() == -1:  # masked label; -1 means do not collect this label
                    continue
                preds.append(pred)
                labels.append(lab)
            predictions_to_append.append(preds)
            labels_to_append.append(labels)

        predictions.extend(predictions_to_append)
        true_labels.append(labels_to_append)

        eval_loss += tmp_eval_loss.mean().item()

        nb_eval_steps += 1
    eval_loss = eval_loss / nb_eval_steps

    pred_tags = [tags_vals[p_i] for p in predictions for p_i in p]
    valid_tags = [tags_vals[l_ii] for l in true_labels for l_i in l for l_ii in l_i]

    return pred_tags

def predict(args, doc_list):
    args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    args.pretrained_model_name = "bert-base-cased"
    args.ner_batch_size = 32
    args.ner_max_len = 128

    tokenizer = BertTokenizer.from_pretrained(args.pretrained_model_name)

    process_field = get_process_field(args.root)

    tags_vals = NerProcessor().get_labels()
    label_map = {}
    for (i, label) in enumerate(tags_vals):
        label_map[label] = i

    model = CoNLLClassifier.from_pretrained(args.pretrained_model_name,
                                            num_labels=len(label_map)).to(args.device)

    logger.info("Loading model from {}".format(args.ner_model_path))
    model.load_state_dict(torch.load(args.ner_model_path, map_location=args.device), strict=False)

    test_examples = NerProcessor().get_test_examples(doc_list, process_field)

    test_dataset = NERDataSet(data_list=test_examples, tokenizer=tokenizer, label_map=label_map, max_len=args.ner_max_len)

    test_iter = data.DataLoader(dataset=test_dataset,
                                batch_size=args.ner_batch_size,
                                shuffle=False,
                                num_workers=4)

    pred_tags = eval(test_iter, model, args)

    #sentence token
    list_temp = []
    for i in test_examples:
        list_temp.extend(i.text.split(" "))

    temp = []
    ner_info = []
    for index in range(0,len(pred_tags)):
        if list_temp[index] != "-DOCTEMP-":
            if pred_tags[index] != "O":
                temp.append("[{}:{}]".format(list_temp[index],pred_tags[index]))
        else:
            ner_info.append(temp)
            temp = []

    #write in txt
    with open("./../ner_pred_out.txt", "w", encoding='utf-8') as w:
        for text, pred in zip(list_temp, pred_tags):
            w.write("{}\t{}\n".format(text,pred))
    
    for indx in range(len(doc_list)):
        doc_list[indx]["NER"] = ner_info[indx]

    return doc_list
