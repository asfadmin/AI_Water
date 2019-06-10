from typing import List

import hypothesis.strategies as st


def model_component():
    return st.text(
        alphabet=st.characters(
            blacklist_categories=('Cs', ), blacklist_characters=('\n', ':')
        ),
        min_size=1
    )


def classes(elements: List[str] = ['water', 'not_water', 'skip', 'invalid']):
    return st.sets(st.sampled_from(elements))
