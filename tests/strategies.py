import hypothesis.strategies as st


def model_component():
    return st.text(
        alphabet=st.characters(
            blacklist_categories=('Cs', ), blacklist_characters=('\n')
        ),
        min_size=1
    )
