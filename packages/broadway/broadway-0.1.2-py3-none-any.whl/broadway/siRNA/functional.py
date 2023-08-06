"""
selection of functional SiRNA sequence
1. Ui-Tei rules
2. Reynolds rules
3. Amarzguioui rules
"""


def UiTei(seq, verbose=False):
    if not isinstance(seq, str):
        raise TypeError('RNA sequence MUST be string')
    seq = seq.lower()
    # rule 1:
    rule1 = seq[0] in ('a', 'u', 't')
    # rule 2:
    rule2 = seq[18] in ('g', 'c')
    # rule 3:
    au_richness = 0
    for i in range(7):
        if seq[i] in ('a', 'u', 't'):
            au_richness += 1
    rule3 = au_richness >= 4
    # rule 4:
    gc_stretch = 0
    gc_stretch_ = 0
    for i in range(len(seq)):
        if seq[i] in ('g', 'c'):
            gc_stretch_ += 1
        else:
            gc_stretch = max(gc_stretch, gc_stretch_)
            gc_stretch_ = 0
    rule4 = gc_stretch < 10
    if verbose:
        print(rule1, rule2, rule3, rule4, 'au_rich:', au_richness, 'gc_stretch:', gc_stretch)
    properties = {
        'au_richness': au_richness,
        'gc_stretch': gc_stretch
    }
    return (rule1, rule2, rule3, rule4), properties


# rule 3: internal repeats not sure -> guess it should be complimentary exists in orignal
def Reynolds(seq, fullseq=None, verbose=False):
    if not isinstance(seq, str):
        raise TypeError('RNA sequence MUST be string')
    seq = seq.lower()
    if fullseq is not None:
        fullseq = fullseq.lower()
    # seq is guide sequence, which is a reverse complimentary sequence of fullseq
    # rule 1:
    gc_content = 0
    for s in seq:
        if s in ('c', 'g'):
            gc_content += 1
    gc_content /= len(seq)
    rule1 = gc_content >= 0.3 and gc_content <= 0.52
    # rule 2:
    au_richness = 0
    for i in range(5):
        if seq[i] in ('a', 'u', 't'):
            au_richness += 1
    rule2 = au_richness >= 3
    # rule 3:
    rule3 = False
    if fullseq is not None:
        rule3 = seq not in fullseq
    # rule 4:
    rule4 = seq[0] in ('u', 't')
    # rule 5:
    rule5 = seq[16] == 'a'
    # rule 6:
    rule6 = seq[9] == 'a'
    # rule 7:
    rule7 = seq[0] in ('a', 'u')
    # rule 8:
    rule8 = seq[6] != 'c'
    properties = {
        'gc_content': gc_content,
        'au_richness_1_5': au_richness
    }
    if verbose:
        print('Rule 1-4 5-8: %d%d%d%d %d%d%d%d' %(
            rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8
        ))
    return (rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8), properties


def Amarzguioui(seq, verbose=False):
    """
    Most rules are duplicated with UiTei and Reynolds, thus omit here and assume they are all passed
    :param seq:
    :param verbose:
    :return:
    """
    if not isinstance(seq, str):
        raise TypeError('RNA sequence MUST be string')
    seq = seq.lower()
    # rule 1:
    # TODO: how to calculate stable and unstable?
    rule1 = True
    pass
    # rule 2:
    # covered by Ui-Tei rule 2
    rule2 = True
    pass
    # rule 3:
    rule3 = seq[13] in ('a', 'u', 't')
    # rule 4:
    # covered by Ui-Tei rule 1
    rule4 = True
    pass
    # rule 5:
    # covered by Ui-Tei rule 2
    rule5 = True
    pass
    # rule 6:
    # covered by Ui-Tei rule 1
    rule6 = True
    pass
# rule1 TBD
    properties = {}
    return (rule1, rule2, rule3, rule4, rule5, rule6), properties
