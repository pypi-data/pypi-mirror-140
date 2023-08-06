def get_dont_match_prefix_regex(dont_match_prefixes, match_prefix=''):
    return rf"^(?!{'|'.join(dont_match_prefixes)})^{match_prefix}"
