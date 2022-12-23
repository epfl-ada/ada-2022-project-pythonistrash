# ADA Milestone 3 README

## Cracking the Hollywood interview :clapper:

**Link to the datastory: [click here: https://dicedead.github.io/cracking-the-hollywood-interview/](https://dicedead.github.io/cracking-the-hollywood-interview/).**

### Abstract :bulb:

On average, the production of a major box office movie costs $65 million, without counting the marketing and distribution fees [^1]. Unlike house construction, which usually ends up exactly like the pre-sketched plan, making a movie is unpredictable and anticipating the audience’s opinion is nearly impossible despite the effort and money spent.

Thus, producing a movie the right way is a crucial job that requires long studies and decision-making about the relevant parts that define the film. This includes the storyline, the script, the actors, the budget, and many more features. 

This motivates our goal of studying the successful and failed films in terms of public ratings (collected through the IMDb database) and box office revenue. We mainly analyze the different characteristics that define a movie in order to come up with a set of criteria that, if present, will more likely make a movie successful. Additionally, since a high rating might not necessarily imply high revenue, we will investigate how to optimize each metric independently.

### Research Questions :interrobang:
* How do movie genre, country and language affect a movie's success?
* How do actors and their interactions contribute to their movie's success?
* What characterizes a successful and an unsuccessful movie plot?
* Finally, how does rating relate to revenue, if it does at all?

### Proposed additional datasets :chart_with_upwards_trend:

Due to the big size of the additional databases, we put them in the following drive: [link](https://drive.google.com/drive/folders/1ZD2JSEczQqj_R4SoJ3CPIQ2Xg4TF1FOC?usp=sharing). IMDb databases' schemas are described [here](https://www.imdb.com/interfaces/).

#### imdb_title_basics.tsv (782MB)
Contains basic info on movies. Joined with ``imdb_title_ratings.tsv`` on the index `tconst` prior to joining all with ``movie.metadata.tsv``. It is used as the source of new information and as a tool to assess and improve the consistency of the CMU dataset.

#### imdb_title_ratings.tsv (21MB)
Contains the IMDb ratings and votes information for IMDb movies. It is joined with ``movie.metadata.tsv`` according to the movies titles and release years.

#### imdb_name_basics.tsv (705MB)
Contains the IMDb actors and actress information. It is used as an additional source for actor data analysis.

#### imdb_title_principals.tsv (2.33GB)
Contains the IMDb casting data. Will be applied for Method 2 in Milestone 3.

#### boxoffice.csv (623KB)
Contains a set of 15737 movies ranked by revenue along with the studio and release year. The main purpose of this dataset is to fill the NaN values in the ``Movie box office revenue`` field of the CMU dataset. This is justified by the importance of this feature in our study.

### Methods :hammer_and_wrench: 
At this early stage of the project, our goal is to explore all aspects of the data at our disposal. We have divided the work in a data-type-driven approach in order to best target the research questions addressed above.


**0. Preprocessing and cleaning**
Firstly, since ratings are absent from the given dataset, we had to merge an IMDb dataset containing that information with the given CMU dataset, cleaning the data in the process.

**1. How does movie genre, country and language affect a movie's success?**

For this, we have extracted individual genres, countries and languages from the JSON-like given lists for each movie, appending indicator variables to the global dataframe of movies' metadata. Thanks to these, we have plotted revenue and rating histograms conditioned on each of the (frequent) genres, countries and languages.

Later, we will examine how combinations of these three features influence rating and revenue, as well as combinations of these three with other ones such as the release year. We will also conduct a time series analysis to see the effect of time on the dependencies between these three features and both success metrics.

**2. How do actors and their interactions contribute in their movie's success?** 

Thanks to IMDb actors and casting databases, we can gather the castings of films and create a graph representing interactions between actors. Nodes represent actors and edges "has worked with"-relationships. Edges can also be weighted in terms of the number of collaborations between two people. Additionally, we will investigate if there exist clusters in the graph by applying k-means and spectral clustering methods.

With this information, we will study how revenue and rating success depend on both individual and group participation of actors. We will train an ML model with input data generated from previous information and its interactions. Those models can be linear regression, for to obtain direct insights from feature weights, or more performant techniques such as Decision Trees combined with AI explainability tools (LIME and SHAP).

**3. What characterizes a successful and an unsuccessful movie plot?**

To tackle this task, we use the already tokenised and stemmed plots in order to analyse the type of plots that characterise movies with high revenue and ratings. Practically speaking, we will use TF-IDF and plot embeddings computed using the Word2Vec algorithm to be able to compare the texts and come up with words and topics that characterize successful movies' plots.

**4. How does rating relate to revenue, if it does at all?**

The answer to this question would be an aggregation of the previous findings and thus a conclusion to our project. In other words, after having found what are the general features that influence the success of a movie, we will analyse how the latte differ when we measure the success by rating and by revenue respectively.

### Proposed timeline :date:
We set up six sprints, the first one matching the deadline for milestone 2 and the last one corresponding to the final submission.

* 18/11/22 : method 0
* 25/11/22 : rest of method 1
* 02/12/22 : method 2 
* 09/12/22 : method 3 & data story draft
* 16/12/22 : method 4 & website draft
* 23/12/22 : finish data story, website and review 


### Organization within the team :pushpin:
* Datastory: Everybody
* Website UI: Raymond and Hind
* Visualizations: Javier and Salim
* Methods: Salim for method 1, Javier for 2, Raymond for 3, Hind for method 4


[^1]: <https://www.investopedia.com/financial-edge/0611/why-movies-cost-so-much-to-make.aspx>
