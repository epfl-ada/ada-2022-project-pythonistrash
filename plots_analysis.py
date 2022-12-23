from base_imports import *
from metadata_analysis import *

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


def find_more_or_less_successful_wrt(df, metric, values, value_prefix, q_low=0.1, q_high=0.9) -> dict:
    """
    Outputs a dictionary of format: 'value': (least successful movies, most successful movies)

    :param metric: success metric
    :param values: values to consider (genre, lang, country)
    :param value_prefix: str
    :param q_low: quantile below which a movie is among the least successful
    :param q_high: similar to q_high for most successful
    :return: said dict
    """

    values_dfs = {}
    for val in values:
        contains_val = df[name_appended_column(value_prefix, val)] == 1
        df_contains_val = df[contains_val]

        lo_q = df_contains_val[metric].quantile(q=q_low)
        hi_q = df_contains_val[metric].quantile(q=q_high)

        val_less_success = df_contains_val[df_contains_val[metric] <= lo_q]
        val_more_success = df_contains_val[df_contains_val[metric] >= hi_q]

        values_dfs[val] = (val_less_success, val_more_success)

    return values_dfs


def get_successful(x):
    return x[1]


def get_unsuccessful(x):
    return x[0]


def get_term_topic_matrix(df: pd.DataFrame, nbr_topics=5, lemmas_col='important_lemmas') -> \
        tuple[pd.DataFrame, list[float]]:
    """
    Compute LSA of given data: SVD (tfidf(data) = USV^T) then return V^T and S

    :param df: pd.Dataframe, data with lemmas to be TF-IDF then LSA processed
    :param nbr_topics: int, number of latent topics to be
    :param lemmas_col: str, column where to find lemmas
    :return: tuple containing V^T as a dataframe with columns corresponding to latent topics and rows as words,
             and S containing singular values
    """
    tfidf_vectorizer = TfidfVectorizer(tokenizer=lambda x: x, lowercase=False)
    tfidf_df = pd.DataFrame(tfidf_vectorizer.fit_transform(df[lemmas_col]).toarray(),
                            columns=tfidf_vectorizer.get_feature_names_out())
    lsa = TruncatedSVD(n_components=nbr_topics, n_iter=100, random_state=42)
    lsa.fit_transform(tfidf_df)
    v_T = lsa.components_.T
    term_topic_matrix = pd.DataFrame(data=v_T, index=tfidf_df.columns,
                                     columns=[f'topic {i}' for i in range(0, v_T.shape[1])])
    return term_topic_matrix, lsa.singular_values_


def top_m_words_nth_topic(term_topic_matrix: pd.DataFrame, nth_topic: int, suffix: str, m_words=10,
                          plot=True) -> pd.Series:
    """
    Retrieve most important m words in topic n

    :param term_topic_matrix: output V^T of previous function
    :param nth_topic: index of topic
    :param suffix: str, in plot title
    :param m_words: number of words
    :param plot: bool, plots importance of top m words or not
    :return: Series containing the m words and their importance
    """
    top_m_terms = term_topic_matrix[f'topic {nth_topic}'].sort_values(ascending=False)[:m_words + 1]
    if len(top_m_terms[top_m_terms.index == "be"]) > 0:
        top_m_terms.drop("be", inplace=True)
    top_m_terms = top_m_terms[:m_words]
    if plot:
        plt.title(f'Top {m_words} terms in topic {nth_topic} for movies of {suffix}')
        sns.barplot(x=top_m_terms.values, y=top_m_terms.index)
    return top_m_terms


def topic_piemaker(importance_ser: pd.Series, title: str, colors=px.colors.sequential.Greens_r) -> Figure:
    """
    Create pie of words for a topic
    :param importance_ser: importance series corresponding to words
    :param title: pie title
    :param colors: color palette
    :return: Figure object, to be converted to html
    """
    temp_df = pd.DataFrame(data={"Importance": importance_ser})
    temp_df["Word"] = temp_df.index

    fig = px.pie(temp_df,
                 title=title,
                 names="Word",
                 values="Importance",
                 color="Importance",
                 color_discrete_sequence=colors,
                 hole=0.3,
                 labels="Word"
                 )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def savepie(fig: Figure, genre: str, metric: str, successful: int, idx_topic: int) -> None:
    """
    Save topic pie to disk
    :param fig: Figure object
    :param genre: str
    :param metric: str
    :param successful: 1 if topic is a successful one, anything else otherwise
    :param idx_topic: int
    """
    successfulness_string = 'succ' if successful == 1 else 'fail'
    with open(f"outputs/plot_analysis/{genre[:4]}_{metric}_{successfulness_string}_topic_{idx_topic + 1}.svg",
              "wb") as f:
        f.write(fig.to_image(format="svg"))
