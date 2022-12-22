from base_imports import *


def get_title_by_index(index):
    """
    Returns the title id at a given index
    :param index: The id index in the list of ids
    :return: The id
    """

    def f(array):
        list_ids = array.split(",")
        corresponding_id = ""
        if index < len(list_ids):
            corresponding_id = list_ids[index]
        return corresponding_id

    return f


def assign_known_title(index, actors_df, names_df):
    """
    Fetch the known titles names
    :param index: Index of the title in the list
    :param actors_df: actors dataframe
    :param names_df: movie names dataframe
    :return:
    """
    actors_df = actors_df.merge(names_df, left_on="knownForTitles{}".format(index), right_on='tconst', how='inner')
    actors_df["knownForTitles{}".format(index)] = actors_df['primaryTitle']
    actors_df = actors_df.drop('tconst', axis=1)
    actors_df = actors_df.drop('primaryTitle', axis=1)
    return actors_df


def is_actor(professions):
    return str(professions) == "actor" or str(professions) == "actress"


def get_metadata_df_from_genre(genre, metadata, do_filter=False, filter_on_revenue=True, n_filter=1000):
    # Returns dataframe of movies' metadata for films assigned to the given genre
    df = metadata[metadata["genre: " + genre] == 1][['Wikipedia movie ID', 'primaryTitle', 'originalTitle',
                                                     'Movie genres: values', 'Movie box office revenue',
                                                     'averageRating']]
    print("Number of films for genre", genre, ":", df.shape[0])

    # Select top n_filter films by revenue (filter_on_revenue == true) or by rating (filter_on_revenue == false)
    if do_filter:
        if filter_on_revenue:
            filter_column = 'Movie box office revenue'
        else:
            filter_column = 'averageRating'

        df = df.sort_values(filter_column, ascending=False).head(n_filter)
        print("Number of films for genre ", genre, "(max 1000 after filter) :", df.shape[0])

    return df


def merge_characters_films(characters, movies):
    # Merge character dataframe with movies' metadata dataframe
    df = characters.merge(movies, left_on='Wikipedia movie ID', right_on='Wikipedia movie ID', how='inner')

    print("After merging, number of characters:", df.shape[0])

    nb_actors = df['Freebase actor ID'].nunique()
    print("After merging, number of actors:", nb_actors)

    nb_movies = df['Wikipedia movie ID'].nunique()
    print("After merging, number of films:", nb_movies)

    return df, nb_actors


def create_graph(char_df, genre, nb_actors, weight_on_revenue=True):

    # Array that maps an index (identifier) to an actor ID and actor name
    array_actors = char_df['Freebase actor ID'].unique()
    for idx, actor_id in enumerate(array_actors):
        array_actors[idx] = (actor_id, char_df[char_df['Freebase actor ID'] == actor_id].iloc[0]['Actor name'])

    # dict_actors maps an actor ID to the index in array_actors
    dict_actors = {}
    for idx, actor in enumerate(array_actors):
        dict_actors[actor[0]] = idx

    print("Created array and dictionary of actors. First 5 entries of array_actors:")
    print(array_actors[:5])

    # Initialize the adjacency matrix for the graph
    adjacency_matrix = np.zeros(shape=(nb_actors, nb_actors))

    # Pandas groupby object of characters grouped by film
    characters_by_film_df = char_df.groupby(["Wikipedia movie ID"])
    print("Grouped characters by film")

    # We add an edge or increase its weight if the edge already exists
    # between two distinct actors that have played in the same film.
    # Having worked on the same film contributes to the weight between two actors
    # by the revenue (in millions) or rating of the film.
    for film in characters_by_film_df.groups.keys():
        characters = characters_by_film_df.get_group(film)

        # Prevents from counting multiple times actors that contribute
        # as different characters in a same film
        set_pair_actors = set()

        for i, character_i in characters.iterrows():
            for j, character_j in characters.iterrows():

                from_index = dict_actors[character_i['Freebase actor ID']] # (from) actor idx in array_actors
                to_index = dict_actors[character_j['Freebase actor ID']] # (to) actor idx in array_actors
                hash_couple_actors = str(from_index)+"-"+str(to_index)
                if hash_couple_actors in set_pair_actors:
                    continue
                else:
                    set_pair_actors.add(hash_couple_actors)

                if from_index < to_index:
                    if weight_on_revenue:
                        adjacency_matrix[from_index][to_index] += character_i['Movie box office revenue']/1000000.
                    else:
                        adjacency_matrix[from_index][to_index] += character_i['averageRating']

    print("Populated adjacency matrix")

    # Open graph csv file and write column headers
    # TODO
    with open("data/graphs/graph_" + "action_adventure" + ".csv", 'w', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(["Source", "Target", "Weight"])

        nb_edges = 0

        # Add edges to the file
        for from_ in range(nb_actors):
            for to_ in range(from_+1, nb_actors):
                # nodes in graph are represented by actor names
                from_name = array_actors[from_][1]
                to_name = array_actors[to_][1]

                weight = adjacency_matrix[from_][to_]
                if weight != 0:
                    csv_writer.writerow([from_name, to_name, weight]) # WE HAVE DUPLICATES IN THE NAMES!
                    nb_edges += 1

    print("Created graph csv file, number of edges:", nb_edges)