
import os
from pickle import TRUE
import torch
from .dataset import load_data
from .extract import extract
from .model import BERTBiLSTM

def get_process_field(root):
    process_field = []
    for child in root.iter("ProcessField"):
        for i in child:
            process_field.append(i.attrib.get("name"))
    return process_field

def get_models(bert_config,
               pred_n_labels=3,
               arg_n_labels=9,
               n_arg_heads=8,
               n_arg_layers=4,
               lstm_dropout=0.3,
               mh_dropout=0.1,
               pred_clf_dropout=0.,
               arg_clf_dropout=0.3,
               pos_emb_dim=64,
               use_lstm=False,
               device=None):
    return BERTBiLSTM(
            bert_config=bert_config,
            lstm_dropout=lstm_dropout,
            pred_clf_dropout=pred_clf_dropout,
            arg_clf_dropout=arg_clf_dropout,
            pos_emb_dim=pos_emb_dim,
            pred_n_labels=pred_n_labels,
            arg_n_labels=arg_n_labels).to(device)

def data_to_sentence(doc_list, process_field):
    data = []
    for doc in doc_list:
        for field in process_field:
            data.extend(doc[field].split("."))
        data.append("-DOCTEMP-")
    data = [i for i in data if i]
    return data


def predict(args, doc_list):
    args.save_path = "./../"
    args.bert_config = 'bert-base-cased'
    args.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    args.visible_device = "0"
    args.batch_size = 1
    args.pos_emb_dim = 64
    args.n_arg_heads = 8
    args.n_arg_layers = 4
    args.use_lstm = True
    args.binary = False

    args.pred_n_labels = 3
    args.arg_n_labels = 9
    os.environ["CUDA_VISIBLE_DEVICES"] = args.visible_device

    model = get_models(
        bert_config=args.bert_config,
        pred_n_labels=args.pred_n_labels,
        arg_n_labels=args.arg_n_labels,
        n_arg_heads=args.n_arg_heads,
        n_arg_layers=args.n_arg_layers,
        pos_emb_dim=args.pos_emb_dim,
        use_lstm=args.use_lstm,
        device=args.device)

    model.load_state_dict(torch.load(args.oie_model_path, map_location=args.device), strict=False)
    model.zero_grad()
    model.eval()

    process_field = get_process_field(args.root)
    data = data_to_sentence(doc_list, process_field)


    loader = load_data(
        data=data,
        batch_size=args.batch_size,
        tokenizer_config=args.bert_config,
        train=False)

    oie = extract(args, model, loader, args.save_path)
    for idx in range(len(doc_list)):
        doc_list[idx]['OIE'] = oie[idx]

    return doc_list




