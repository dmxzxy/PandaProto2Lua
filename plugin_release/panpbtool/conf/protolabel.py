
class LabelType:
    LABEL_OPTIONAL      = 1
    LABEL_REQUIRED      = 2
    LABEL_REPEATED      = 3

LabelName = {
    LabelType.LABEL_OPTIONAL   : 'optional',
    LabelType.LABEL_REQUIRED   : 'required',
    LabelType.LABEL_REPEATED   : 'repeated',
}

def is_required(label):
    return label == LabelType.LABEL_REQUIRED

def is_optional(label):
    return label == LabelType.LABEL_OPTIONAL

def is_repeated(label):
    return label == LabelType.LABEL_REPEATED

def get_name(label):
    return LabelName[label]