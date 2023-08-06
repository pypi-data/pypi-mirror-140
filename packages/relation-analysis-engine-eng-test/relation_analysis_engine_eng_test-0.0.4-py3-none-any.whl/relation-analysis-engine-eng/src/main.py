import xml.etree.ElementTree as ET
import time, os, argparse
from scd_parser import scd_validation,parser_main
from bert_ner import predict as ner
from bert_oie import test as oie


def main(args):

    tree = ET.parse(args.config_path)
    args.root = tree.getroot()
    

    scd_validation.validation_main(args.root)

    doc_list = parser_main.parser_main(args)  

    if args.predict_ner:
        doc_list = ner.predict(args, doc_list)

    if args.predict_oie:
        doc_list = oie.predict(args, doc_list)

    if args.save_output:
        with open(os.path.join(".\..","output.txt"),"w",encoding='UTF-8') as r:
            for i in doc_list:
                r.write(str(i))
                r.write("\n\n")


if __name__=="__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--config_path", type=str, default="./../config/config.xml",
                        help="패키지의 config.xml의 상대경로")

    parser.add_argument("--cleaning", action="store_true", help="특수 문자 제거를 원한다면 입력")
    parser.add_argument("--save_output", action="store_false", help="OUTPUT저장을 원하지 않으면 입력")

    parser.add_argument("--predict_ner", action="store_true", help="ner 값 예측을 원한다면 입력")
    parser.add_argument("--ner_model_path", type=str, default="./bert_ner/model/model.torch")

    parser.add_argument("--predict_oie", action="store_true", help="oie 값 예측을 원한다면 입력")
    parser.add_argument('--oie_model_path', default='./bert_oie/model/model-epoch1-end-score1.9670.bin')



    args = parser.parse_args()

    main(args)
