def adduep(udict, edict, pdict):
    """Consolidate dictionaries containing user, email, password errors
    """
    #TODO: generalize this for an arbitrary number of dicts
    errors = dict(
        (n, udict.get(n, '') + pdict.get(n, '') + edict.get(n, ''))
            for n in set(udict)|set(pdict)|set(edict)
    )
    return errors



def add_dicts(*dicts):
    """add an arbitrary number of dictionaries together
    """
    d = {}
    for x in dicts:
        d.update(x)
    return d

