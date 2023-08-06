def complimentary(seq, reverse=False, uppercase=False, seq_type='RNA'):
    if not isinstance(seq, str):
        raise TypeError('RNA sequence MUST be string')
    # convert to lower case for simplicity
    seq = seq.lower()
    # complimentary sequence
    complimentary_seq = ''
    for s in seq:
        if s == 'c':
            complimentary_seq += 'g'
        elif s == 'g':
            complimentary_seq += 'c'
        elif s == 'a':
            if seq_type == 'RNA':
                complimentary_seq += 'u'
            elif seq_type == 'DNA':
                complimentary_seq += 't'
        elif s in ('u', 't'):
            complimentary_seq += 'a'
        else:
            raise ValueError('cannot understand:', s)
    # reverse the sequence if necessary: abc -> cba
    if reverse:
        complimentary_seq = complimentary_seq[::-1]
    if uppercase:
        complimentary_seq = complimentary_seq.upper()
    return complimentary_seq
