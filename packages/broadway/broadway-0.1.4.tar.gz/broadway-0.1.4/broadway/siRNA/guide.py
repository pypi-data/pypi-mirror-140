from broadway.utils.complimentary import complimentary


def get_all_guide(seq, design_len=21):
    """
    Get all guide strand from full sequence
    :param seq:
    :param design_len:
    :return:
    """
    if not isinstance(seq, str):
        raise TypeError('RNA sequence MUST be string')

    guide_seqs = []
    for i in range(len(seq)-design_len+1):
        seq_cp = complimentary(seq[i:i+design_len])
        guide_seqs.append(seq_cp[::-1])
    return guide_seqs
