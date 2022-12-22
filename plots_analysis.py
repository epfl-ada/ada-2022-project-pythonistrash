from base_imports import *


subpath = "data/corenlp_plot_summaries/"
starting_positions = {"VB", "NN", "NP", "PP", "RB"}

def get_important_lemmas(wiki_id: int) -> list[str]:
    """
    Retrieve important lemmas from
    :param wiki_id: wikipedia movie id
    :return: list of lemmas of important words
    """

    def is_important(token):
        tok = token.find("POS").text
        for pos in starting_positions:
            if tok.startswith(pos):
                return True
        return False

    def to_lemma(token):
        return token.find("lemma").text

    zip_name = str(wiki_id) + ".xml.gz"

    if not os.path.isfile(subpath + zip_name):
        print(f"Missing file with id {wiki_id}")
        return []

    with gzip.open(subpath + zip_name, 'r') as file:
        xmltree = ET.ElementTree(ET.fromstring(file.read())).getroot()

    return list(map(to_lemma, filter(is_important, xmltree.iter("token"))))