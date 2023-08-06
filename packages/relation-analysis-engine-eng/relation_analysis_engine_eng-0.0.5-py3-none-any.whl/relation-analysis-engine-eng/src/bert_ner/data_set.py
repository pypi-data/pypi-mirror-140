

import torch
from torch.utils import data


class InputExample(object):
    """A single training/test example for simple sequence classification."""

    def __init__(self, guid, text, label=None, segment_ids=None):
        """Constructs a InputExample.
        Args:
          guid: Unique id for the example.
          text_a: string. The untokenized text of the first sequence. For single
            sequence tasks, only this sequence must be specified.
          label: (Optional) string. The label of the example. This should be
            specified for train and dev examples, but not for test examples.
        """
        self.guid = guid
        self.text = text
        self.label = label
        self.segment_ids = segment_ids

#doclist로 input할시 doc간의 구분이 안된다
def readfile(doc_list, process_field):
    data = []

    for doc in doc_list:
        temp = []
        for field in process_field:
            temp.append(doc[field])
        doc_text = ".".join(temp).split(".")
        for i in doc_text:
            if i != '':
                sentence = i.strip().split()
                label = ["O"]*len(sentence)
                data.append((sentence, label))
        sentence = ["-DOCTEMP-"]
        label = ["O"]*len(sentence)
        data.append((sentence, label))
    return data

def readfile_(doc, process_field):
    data = []
    temp = []

    for field in process_field:
        temp.append(doc[field])
    doc_text = ".".join(temp).split(".")
    for i in doc_text:
        if i != '':
            sentence = i.strip().split()
            label = ["O"]*len(sentence)
            data.append((sentence, label))
    return data


class DataProcessor(object):
    """Base class for data converters for sequence classification data sets."""
    def get_labels(self):
        """Gets the list of labels for this data set."""
        raise NotImplementedError()

    @classmethod
    def _read_tsv(cls, doc_list, process_field, quotechar=None):
        """Reads a tab separated value file."""
        return readfile(doc_list, process_field)

class NerProcessor(DataProcessor):
    """Processor for the CoNLL-2003 data set."""
    def get_test_examples(self, doc_list, process_field):
        """See base class."""
        return self._create_examples(
            self._read_tsv(doc_list, process_field), "test")

    def get_labels(self):
        return ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC",
                "[CLS]", "[SEP]", "X"]

    @staticmethod
    def _create_examples(lines, set_type):
        examples = []
        for i, (sentence, label) in enumerate(lines):
            guid = "%s-%s" % (set_type, i)
            text_a = ' '.join(sentence)
            label = label
            examples.append(InputExample(guid=guid, text=text_a, label=label))
        return examples


class NERDataSet(data.Dataset):
    def __init__(self, data_list, tokenizer, label_map, max_len):
        self.max_len = max_len
        self.label_map = label_map
        self.data_list = data_list
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, idx):
        input_example = self.data_list[idx]
        text = input_example.text
        label = input_example.label
        word_tokens = ['[CLS]']
        label_list = ['[CLS]']
        label_mask = [0]  # value in (0, 1) - 0 signifies invalid token

        input_ids = [self.tokenizer.convert_tokens_to_ids('[CLS]')]
        label_ids = [self.label_map['[CLS]']]

        # iterate over individual tokens and their labels
        for word, label in zip(text.split(), label):
            tokenized_word = self.tokenizer.tokenize(word)

            for token in tokenized_word:
                word_tokens.append(token)
                input_ids.append(self.tokenizer.convert_tokens_to_ids(token))

            label_list.append(label)
            label_ids.append(self.label_map[label])
            label_mask.append(1)
            # len(tokenized_word) > 1 only if it splits word in between, in which case
            # the first token gets assigned NER tag and the remaining ones get assigned
            # X
            for i in range(1, len(tokenized_word)):
                label_list.append('X')
                label_ids.append(self.label_map['X'])
                label_mask.append(0)

        assert len(word_tokens) == len(label_list) == len(input_ids) == len(label_ids) == len(
            label_mask)

        if len(word_tokens) >= self.max_len:
            word_tokens = word_tokens[:(self.max_len - 1)]
            label_list = label_list[:(self.max_len - 1)]
            input_ids = input_ids[:(self.max_len - 1)]
            label_ids = label_ids[:(self.max_len - 1)]
            label_mask = label_mask[:(self.max_len - 1)]

        assert len(word_tokens) < self.max_len, len(word_tokens)

        word_tokens.append('[SEP]')
        label_list.append('[SEP]')
        input_ids.append(self.tokenizer.convert_tokens_to_ids('[SEP]'))
        label_ids.append(self.label_map['[SEP]'])
        label_mask.append(0)

        assert len(word_tokens) == len(label_list) == len(input_ids) == len(label_ids) == len(
            label_mask)

        sentence_id = [0 for _ in input_ids]
        attention_mask = [1 for _ in input_ids]

        while len(input_ids) < self.max_len:
            input_ids.append(0)
            label_ids.append(self.label_map['X'])
            attention_mask.append(0)
            sentence_id.append(0)
            label_mask.append(0)

        assert len(word_tokens) == len(label_list)
        assert len(input_ids) == len(label_ids) == len(attention_mask) == len(sentence_id) == len(
            label_mask) == self.max_len, len(input_ids)
        # return word_tokens, label_list,
        return torch.LongTensor(input_ids), torch.LongTensor(label_ids), torch.LongTensor(
            attention_mask), torch.LongTensor(sentence_id), torch.BoolTensor(label_mask)
