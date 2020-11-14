# Printing total nb and percentage of null

import pandas as pd

def print_null_pct(df):
    tot_null = df.isna().sum().sum()
    print('nb of null: ', tot_null, '\npct of null: ',
        '{:.1f}'.format(tot_null*100/(df.shape[0]*df.shape[1])))

# Plotting heatmap (2 options available, rectangle or triangle )

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt



def plot_heatmap(corr, title, figsize=(8, 4), vmin=-1, vmax=1, center=0,
                 palette=sns.color_palette("coolwarm", 20), shape='rect',
                 fmt='.2f', robust=False, fig=None, ax=None):
    fig = plt.figure(figsize=figsize) if fig is None else fig
    ax = fig.add_subplot(111) if ax is None else ax

    if shape == 'rect':
        mask = None
    elif shape == 'tri':
        mask = np.zeros_like(corr, dtype=np.bool)
        mask[np.triu_indices_from(mask)] = True
    else:
        print('ERROR : this type of heatmap does not exist')

    ax = sns.heatmap(corr, mask=mask, cmap=palette, vmin=vmin, vmax=vmax,
                     center=center, annot=True, annot_kws={"size": 10}, fmt=fmt,
                     square=False, linewidths=.5, linecolor='white',
                     cbar_kws={"shrink": .9, 'label': None}, robust=robust,
                     xticklabels=corr.columns, yticklabels=corr.index,
                     ax=ax)
    ax.tick_params(labelsize=10, top=False, bottom=True,
                   labeltop=False, labelbottom=True)
    ax.collections[0].colorbar.ax.tick_params(labelsize=10)
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right", rotation_mode="anchor")
    ax.set_title(title, fontweight='bold', fontsize=12)



'''Takes the H matrix (topics/words) as a dataframe, extracts the n top words
and plots a wordcloud of the (n_top_words) top words for each topic.
'''

from wordcloud import WordCloud

def plot_wordclouds_topwords(H, n_top_words, n_rows=1, figsize=(18,8),
                             random_state=None):

    fig = plt.figure(figsize=figsize)
    wc = WordCloud(stopwords=None, background_color="black",
                   colormap="Dark2", max_font_size=150,
                   random_state=random_state)
    # boucle sur les thèmes
    for i, topic_name in enumerate(H.index,1):
        ser_10w_topic = H.loc[topic_name]\
            .sort_values(ascending=False)[0:n_top_words]
        wc.generate(' '.join(list(ser_10w_topic.index)))
        n_tot = H.index.shape[0]
        n_cols = (n_tot//n_rows)+((n_tot%n_rows)>0)*1
        ax = fig.add_subplot(n_rows,n_cols,i)
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout()
        plt.title(topic_name, fontweight='bold')
        
    plt.show()

'''
t-SNE wrapper in order to use t-SNE as a dimension reducter as a pipeline step of a 
GridSearch (indeed, tsne doesn't have a transform method but only a fit_transform 
method -> it cannot be applied to another set of data than the one on which it was trained)
'''

from sklearn.manifold import TSNE

class TSNE_wrapper(TSNE):

    def __init__(self, angle=0.5, early_exaggeration=12.0, init='random',
                 learning_rate=200.0, method='barnes_hut', metric='euclidean',
                 min_grad_norm=1e-07, n_components=2, n_iter=1000,
                 n_iter_without_progress=300, n_jobs=None,
                 perplexity=30.0, random_state=None, verbose=0):

        self.angle = angle
        self.early_exaggeration = early_exaggeration
        self.init = init
        self.learning_rate = learning_rate
        self.method = method
        self.metric = metric
        self.min_grad_norm = min_grad_norm
        self.n_components = n_components
        self.n_iter = n_iter
        self.n_iter_without_progress = n_iter_without_progress
        self.n_jobs = n_jobs
        self.perplexity = perplexity
        self.random_state = random_state
        self.verbose = verbose

    def transform(self, X):
        return TSNE().fit_transform(X)

    def fit(self,X):
        return TSNE().fit(X)

'''Computes the projection of the observations of df on the two first axes of
a transformation (PCA, UMAP or t-SNE)
The center option (clustering model needed) allows to project the centers
on the two axis for further display, and to return the fitted model
NB: if the model wa already fitted, does not refit.'''

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from umap import UMAP
from sklearn.manifold import TSNE

def prepare_2D_axes(df, ser_clust=None, proj=['PCA', 'UMAP', 't-SNE'],
                    model=None, centers_on=False, random_state=14):

    dict_proj = dict()

    if centers_on:  # Compute and include the centers in the points
        if model is not None:
            model = model.fit(df) if not is_fitted(model) else model
            # ### all clusterers don't have .cluster_centers method -> changed
            # centers = model.cluster_centers_ 
            # ind_centers = ["clust_" + str(i) for i in range(centers.shape[0])]
            # centers_df = pd.DataFrame(centers,
            #                           index=ind_centers,
            #                           columns=df.columns)
            #### all clusterers don't have .predict/labels_ method -> changed
            if hasattr(model, 'labels_'):
                clust = model.labels_
            else:
                clust = model.predict(df)
        else:
            clust = ser_clust
        # calculation of centers
        centers_df = df.assign(clust=clust).groupby('clust').mean()
        df = df.append(centers_df)

    ## Projection of all the points through the transformations

    # PCA
    if 'PCA' in proj:
        pca = PCA(n_components=2, random_state=random_state)
        df_proj_PCA_2D = pd.DataFrame(pca.fit_transform(df),
                                      index=df.index,
                                      columns=['PC' + str(i) for i in range(2)])
        dict_proj = dict({'PCA': df_proj_PCA_2D})

    # UMAP
    if 'UMAP' in proj:
        umap = UMAP(n_components=2, random_state=random_state)
        df_proj_UMAP_2D = pd.DataFrame(umap.fit_transform(df),
                                       index=df.index,
                                       columns=['UMAP' + str(i) for i in range(2)])
        dict_proj = dict({'UMAP': df_proj_UMAP_2D})

    # t-SNE
    if 't-SNE' in proj:
        tsne = TSNE(n_components=2, random_state=random_state)
        df_proj_tSNE_2D = pd.DataFrame(tsne.fit_transform(df),
                                       index=df.index,
                                       columns=['t-SNE' + str(i) for i in range(2)])
        dict_proj = dict({'t-SNE': df_proj_tSNE_2D})

    # Separate the clusters centers from the other points if center option in on
    if centers_on:
        dict_proj_centers = {}
        for name, df_proj in dict_proj.items():
            dict_proj_centers[name] = dict_proj[name].loc[centers_df.index]
            dict_proj[name] = dict_proj[name].drop(index=centers_df.index)
        return dict_proj, dict_proj_centers, model
    else:
        return dict_proj


''' Plots the points on two axis (projection choice available : PCA, UMAP, t-SNE)
with clusters coloring if model available (grey if no model given).
NB: if the model wa already fitted, does not refit.'''

import seaborn as sns


''' Plots the points on two axis (projection choice available : PCA, UMAP, t-SNE)
with clusters coloring if model available (grey if no model given).
NB: if the model wa already fitted, does not refit.'''

import seaborn as sns

def plot_projection(df, model=None, ser_clust = None, proj='PCA',
                    tw_n_neigh=5, title=None, bboxtoanchor=None,
                    figsize=(5, 3), size=1, palette='tab10',
                    legend_on=False, fig=None, ax=None, random_state=14):

    fig = plt.figure(figsize=figsize) if fig is None else fig
    ax = fig.add_subplot(111) if ax is None else ax

    # a1 - if model : computes clusters, clusters centers and plot with colors
    if model is not None:

        # Computes the axes for projection with centers
        # (uses fitted model if already fitted)
        dict_proj, dict_proj_centers, model = prepare_2D_axes(df,
                                                              proj=[proj],
                                                              model=model,
                                                              centers_on=True,
                                                              random_state=random_state)

        # ...or using model already fitted in prepare_2D_axes to get it
        #### all clusterers don't have .predict/labels_ method -> changed
        if hasattr(model, 'labels_'):
            clust = model.labels_
        else:
            clust = model.predict(df)
        ser_clust = pd.Series(clust,
                                index=df.index,
                                name='Clust')
        
    # a2 - if no model but ser_clust is given, plot with colors
    elif ser_clust is not None:
        
        # Computes the axes for projection
        dict_proj, dict_proj_centers, _ = \
            prepare_2D_axes(df, ser_clust=ser_clust, proj=[proj],
                            model=None, centers_on=True,
                            random_state=random_state)

        n_clust = ser_clust.nunique()
        colors = sns.color_palette(palette, n_clust).as_hex()

    # Computing the global trustworthiness
    trustw = trustworthiness(df, dict_proj[proj],
                            n_neighbors=tw_n_neigh, metric='euclidean')
    # Computing the trustworthiness category by category
    ser_tw_clust = groups_trustworthiness(df, dict_proj[proj], ser_clust,
                                          n_neighbors=tw_n_neigh)

    # b1 - if ser_clust exists (either calculated from model or given)
    if ser_clust is not None:

        # Showing the points, cluster by cluster
        # for i in range(n_clust):
        for i, name_clust in enumerate(ser_clust.unique()):
            ind = ser_clust[ser_clust == name_clust].index
            ax.scatter(dict_proj[proj].loc[ind].iloc[:, 0],
                       dict_proj[proj].loc[ind].iloc[:, 1],
                       s=size, alpha=0.7, c=colors[i], zorder=1)

            # Showing the clusters centers
            ax.scatter(dict_proj_centers[proj].iloc[:, 0].loc[name_clust],
                        dict_proj_centers[proj].iloc[:, 1].loc[name_clust],
                        marker='o', c=colors[i], alpha=0.7, s=150,
                       edgecolor='k',
                       label="{}: {} | tw={:0.2f}".format(i, name_clust,
                                                          ser_tw_clust[name_clust]),
                       zorder=10) # for the labels only
            # Showing the clusters centers labels (number)
            ax.scatter(dict_proj_centers[proj].iloc[:, 0].loc[name_clust],
                        dict_proj_centers[proj].iloc[:, 1].loc[name_clust],
                        marker=r"$ {} $".format(i),#
                        c='k', alpha=1, s=70, zorder=100)
            if legend_on:
                plt.legend().get_frame().set_alpha(0.3)
            if bboxtoanchor is not None:
                plt.legend(bbox_to_anchor=bboxtoanchor)
            else: 
                plt.legend()


    # b2 - if no ser_clust: only plot points in grey
    else:
        # Computes the axes for projection without centers
        dict_proj = prepare_2D_axes(df,
                                    proj=[proj],
                                    centers_on=False,
                                    random_state=random_state)
        # Plotting the point in grey
        ax.scatter(dict_proj[proj].iloc[:, 0],
                   dict_proj[proj].iloc[:, 1],
                   s=size, alpha=0.7, c='grey')

    title = "Projection: " + proj + "(trustworthiness: {:.2f})".format(trustw)\
             if title is None else title
    ax.set_title(title + "\n(trustworthiness: {:.2f})".format(trustw),
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('ax 1'), ax.set_ylabel('ax 2')



''' Takes a pd.Series containing the texts of each description
applies a preprocessing function if given (stopwords, stemming...)
then turn the descriptions in vectors (bow of tf-idf, depending on the avlue of
 tfidf_on)
 returns document term matrix as a dataframe and the list of new excluded words.
'''

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

def compute_doc_terms_df(ser_desc, 
                         preproc_func=None,
                         preproc_func_params=None,
                         vec_params = {'min_df': 1},
                         tfidf_on=False,
                         print_opt=False):

    # ---- Apply a preprocessing function prior to vectorization
    if preproc_func is not None:
        ser_desc = ser_desc.apply(lambda x: preproc_func(x,
                                                         **preproc_func_params))
        ser_desc = ser_desc.apply(lambda x: ' '.join(x))
    else:
        ser_desc = ser_desc
    
    # ---- Vectorization of each of the texts (row)
    if tfidf_on:
        # TF-IDF matrix
        vec = TfidfVectorizer(**vec_params)
    else:
        # BOW matrix (count)
        vec = CountVectorizer(**vec_params)

    doc_term = vec.fit_transform(ser_desc)
    if print_opt:
        print( "Created %d X %d doc_term matrix" % (doc_term.shape[0],
                                                    doc_term.shape[1]))

    # ---- Vocabulary of the document_term matrix
    doc_term_voc = vec.get_feature_names()
    if print_opt:
        print("Vocabulary has %d distinct terms" % len(doc_term_voc))

    # ---- Get the list of the new stop-words
    new_sw = vec.stop_words_
    if print_opt:
        print("Old stop-words list has %d entries" % len(sw) )
        print("New stop-words list has %d entries" % len(new_sw))

    doc_term_df = pd.DataFrame(doc_term.todense(),
                index=ser_desc.index, # each item
                columns=doc_term_voc) # each word

    # document term matrix as a dataframe and the list of new excluded words
    return doc_term_df, new_sw



'''
Takes a vectorized matrix (dataframe) of the documents
(Document-trem matrix: BOW or tf-idf... documents(rows) x words (columns))
and returns the projected vectors in the form of a dataframe
(words (rows) x w2v dimensions(columns))
'''

def proj_term_doc_on_w2v(term_doc_df, w2v_model, print_opt=False):

    # Checking the number of words of our corpus existing in the wiki2vec dictionary
    li_common_words = []
    for word in term_doc_df.columns:
        word_ = w2v_model.get_word(word)
        if word_ is not None:
            li_common_words.append(word)
    if print_opt:
        print(f"The w2v dictionary contains {len(li_common_words)} words out of \
the {term_doc_df.shape[1]} existing in our descriptions,\ni.e. \
{round(100*len(li_common_words)/term_doc_df.shape[1],1)}% of the whole vocabulary.")

    # extracting each of the word vectors
    word_vectors_df = pd.DataFrame()
    for word in li_common_words:
        word_vectors_df[word] = w2v_model.get_word_vector(word)
    word_vectors_df = word_vectors_df.T
    word_vectors_df.columns = ['dim_'+str(i)\
                               for i in range(word_vectors_df.shape[1])]

    # projection of the Document_terms matrix on the wiki2vec
    w2v_emb_df = term_doc_df[li_common_words].dot(word_vectors_df)

    return w2v_emb_df


""" For a each number of clusters in a list ('list_n_clust'),
- runs iterations ('n_iter' times) of a KMeans on a given dataframe,
- computes the 4 scores : silhouette, davies-bouldin, calinski_harabasz and
distortion
- if enabled only('return_pop'): the proportion (pct) of the clusters
for each iteration and number of clusters
- and returns 3 dictionnaries:
    - dict_scores_iter: the 4 scores
    - dict_ser_clust_n_clust: the list of clusters labels for df rows
    - if enabled only (return_pop), 'dict_pop_perc_n_clust' : the proportions

NB: the functions 'plot_scores_vs_n_clust', 'plot_prop_clust_vs_nclust' and
'plot_clust_prop_pie_vs_nclust' plot
respectively:
- the scores vs the number of clusters,
- the proportion of clusters
- and the pies of the clusters ratio,
 based on the dictionnaries provided by compute_clust_scores_nclust"""


from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.cluster import AgglomerativeClustering
from sklearn.ensemble import RandomForestClassifier

def compute_clust_scores_nclust(df, df_fit=None, model=None, n_iter=10, inertia=True,
                                list_n_clust=range(2,8), return_pop=False):
#### ATTENTION AU CAS PAR CAS POUR LES MODELES AUTRES QUE KMEANS

    dict_pop_perc_n_clust = {}
    dict_ser_clust_n_clust = {}
    dict_scores_iter = {}

    df_fit = df if df_fit is None else df_fit
    km_default = True if model is None else False
    ahc = True if model == 'ahc' else False
    gmm = True if model == 'gmm' else False

    # --- Looping on the number of clusters to compute the scores
    for i, n_clust in enumerate(list_n_clust,1):

        silh, dav_bould, cal_harab, distor = [], [], [], []
        pop_perc_iter, ser_clust_iter = pd.DataFrame(), pd.DataFrame()

        # Iterations of the same model (stability)
        for j in range(n_iter):
            if km_default:
                model = KMeans(n_clusters=n_clust,
                               random_state=np.random.randint(100))
            elif ahc:
                ahc = AgglomerativeClustering(n_clusters=n_clust)
                clf = RandomForestClassifier(random_state=np.random.randint(100))
                model = InductiveClusterer(ahc, clf)
            elif gmm:
                # reinitialisation of the random state (gmm)
                model = GaussianMixture(n_components=n_clust,
                                        covariance_type='spherical',
                                        random_state=np.random.randint(100))
            else:
                print("ERROR: unknown model asked")
            model.fit(df_fit)
            ser_clust = pd.Series(data=model.predict(df),
                                  index=df.index,
                                  name="iter_"+str(j))
            ser_clust_iter = pd.concat([ser_clust_iter, ser_clust.to_frame()],
                                       axis=1)

            if return_pop:
                # Compute pct of clients in each cluster
                pop_perc = 100 * ser_clust.value_counts() / df.shape[0]
                pop_perc.sort_index(inplace=True)
                pop_perc.index = ['clust_'+str(i) for i in pop_perc.index]
                pop_perc_iter = pd.concat([pop_perc_iter, pop_perc.to_frame()],
                                          axis=1)
        
            # Computing scores for iterations
            silh.append(silhouette_score(X=df, labels=ser_clust))
            dav_bould.append(davies_bouldin_score(X=df, labels=ser_clust))
            cal_harab.append(calinski_harabasz_score(X=df, labels=ser_clust))
            if inertia: distor.append(model.inertia_)

        dict_ser_clust_n_clust[n_clust] = ser_clust_iter

        if return_pop:
            # dict of the population (pct) of clusters iterations
             dict_pop_perc_n_clust[n_clust] = pop_perc_iter.T

        # Dataframe of the results on iterations
        scores_iter = pd.DataFrame({'Silhouette': silh,
                                    'Davies_Bouldin': dav_bould,
                                    'Calinsky_Harabasz': cal_harab,
                                    })
        if inertia:
            scores_iter['Distortion'] = distor
        dict_scores_iter[n_clust] = scores_iter

    if return_pop:
        return dict_scores_iter, dict_ser_clust_n_clust, dict_pop_perc_n_clust
    else:
        return dict_scores_iter, dict_ser_clust_n_clust


''' Plot the 4 mean scores stored in the dictionnary returned by the function
compute_clust_scores_nclust (dictionnary of dataframes of scores (columns)
for each iteration (rows) of the model and for each number of clusters
in a figure with error bars (2 sigmas)'''

def plot_scores_vs_n_clust(dict_scores_iter, figsize=(15,3)):

    fig = plt.figure(figsize=figsize)
    list_n_clust = list(dict_scores_iter.keys())

    # Generic fonction to unpack dictionary and plot one graph
    def score_plot_vs_nb_clust(scores_iter, name, ax, c=None):
        score_mean = [dict_scores_iter[i].mean().loc[n_score] for i in list_n_clust]
        score_std = np.array([dict_scores_iter[i].std().loc[n_score]\
                            for i in list_n_clust])
        ax.errorbar(list_n_clust, score_mean, yerr=2*score_std, elinewidth=1,
                capsize=2, capthick=1, ecolor='k', fmt='-o', c=c, ms=5,
                barsabove=False, uplims=False)

    li_scores = ['Silhouette', 'Davies_Bouldin',
                 'Calinsky_Harabasz', 'Distortion']
    li_colors = ['r', 'b', 'purple', 'g']

    # Looping on the 4 scores
    i=0
    for n_score, c in zip(li_scores, li_colors):
        i+=1
        ax = fig.add_subplot(1,4,i)
        
        score_plot_vs_nb_clust(dict_scores_iter, n_score, ax, c=c)
        ax.set_xlabel('Number of clusters')
        ax.set_ylabel(n_score+' score')

    fig.suptitle('Clustering score vs. number of clusters',
                fontsize=14, fontweight='bold')
    plt.tight_layout(rect=[0,0,1,0.95])
    plt.show()


''' Plot the proportion (%) of each cluster (columns) returned by the function
compute_clust_scores_nclust (dictionnary of dataframes of the proportion
for each iteration (rows) of the model in one figure with error bars (2 sigmas)'''

def plot_prop_clust_vs_nclust(dict_pop_perc_n_clust, figsize=(15,3)):

    fig = plt.figure(figsize=figsize)
    list_n_clust = list(dict_pop_perc_n_clust.keys())
    

    for i, n_clust in enumerate(list_n_clust, 1):
        n_iter = dict_pop_perc_n_clust[n_clust].shape[0]
        ax = fig.add_subplot(3,3,i)
        sns.stripplot(data=dict_pop_perc_n_clust[n_clust],
                      edgecolor='k', linewidth=1,  ax=ax)
        ax.set(ylim=(0,100))
        ax.set_ylabel("prop. of the clusters (%)")
    fig.suptitle(f"Proportion of the clusters through {n_iter} iterations",
                fontweight='bold', fontsize=14)
    plt.tight_layout(rect=[0,0,1,0.97])


""" Plot pies of the proportion of the clusters using the proportions
stored in the dictionnary returned by the function
'compute_clust_scores_nclust' (dictionnary of dataframes of the
proportions (columns) for each iteration (rows) of the model
and for each number of clusters in a figure with error (+/-2 sigmas)"""

def plot_clust_prop_pie_vs_nclust(dict_pop_perc_n_clust,
                                  list_n_clust, figsize=(15, 3)):

    fig = plt.figure(figsize=figsize)

    for i, n_clust in enumerate(list_n_clust,1):
        ax = fig.add_subplot(str(1) + str(len(list_n_clust)) + str(i))

        mean_ = dict_pop_perc_n_clust[n_clust].mean()
        std_ = dict_pop_perc_n_clust[n_clust].std()
        
        wedges, texts, autotexts = ax.pie(mean_,
                autopct='%1.0f%%',
                labels=["(+/-{:.0f})".format(i) for i in std_.values],
                pctdistance=0.5)
        plt.setp(autotexts, size=10, weight="bold")
        plt.setp(texts, size=8)
        ax.set_title(f'{str(n_clust)} clusters')  # , pad=20

    fig.suptitle('Clusters ratio', fontsize=16, fontweight='bold')
    plt.show()


''' Plots on the left the silhouette scores of each cluster and
on the right the projection of the points with cluster labels as cluster'''

from sklearn.metrics import silhouette_score, silhouette_samples

def silh_scores_vs_n_clust(df, n_clust, proj='PCA',
                           xlim=(-0.1, 0.8), figsize=(18, 3), palette='tab10'):
    
    palette = sns.color_palette(palette, np.max(n_clust))
    colors = palette.as_hex()

    distor = []
    for n in n_clust:
        fig = plt.figure(1, figsize=figsize)

        # --- Plot 1: Silhouette scores
        ax1 = fig.add_subplot(121)

        model = KMeans(n_clusters=n, random_state=14)
        model = model.fit(df)

        ser_clust = pd.Series(model.predict(df),
                              index=df.index,
                              name='Clust')
        distor.append(model.inertia_)
        sample_silh_val = silhouette_samples(df, ser_clust)

        y_lower = 10
        # colors = [colors[x] for x in ser_clust.astype('int')]
        for i in range(n):
            # Aggregate and sort silh scores for samples of clust i
            clust_silh_val = sample_silh_val[ser_clust == i]
            clust_silh_val.sort()
            size_clust = clust_silh_val.shape[0]
            y_upper = y_lower + size_clust
            ax1.fill_betweenx(np.arange(y_lower, y_upper),
                              0,
                              clust_silh_val,
                              facecolor=colors[i],
                              edgecolor=colors[i],
                              alpha=0.7)

            # Label of silhouette plots with their clust. nb. at the middle
            ax1.text(-0.05, y_lower + 0.5 * size_clust, str(i))

            # Computes the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        silhouette_avg = silhouette_score(df, ser_clust)
        ax1.set_title("Nb of clusters: {} | Avg silhouette: {:.3f}" \
                      .format(n, silhouette_avg), fontsize=12)
        ax1.set_xlabel("Silhouette coeff. values")
        ax1.set_ylabel("Cluster label")

        # The vertical line for average silhouette score of all the values
        ax1.axvline(x=silhouette_avg, color="red", linestyle="--")
        ax1.set_yticks([])  # Clear the yaxis labels / ticks
        ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])
        ax1.set_xlim(list(xlim))
        # (n+1)*10: inserting blank spaces between clusters silh scores
        ax1.set_ylim([0, df.shape[0] + (n + 1) * 10])

        # --- Plot 2: Showing clusters on chosen projection
        ax2 = fig.add_subplot(122)
        # uses already fitted model
        plot_projection(df, model=model,
                        proj=proj,
                        palette=palette,
                        fig=fig, ax=ax2)

        ax2.set_title('projection: ' + proj, fontsize=12)

        plt.suptitle("Silhouette analysis for {} clusters".format(n),
                     fontsize=14, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()


''' Generates the list of all unique combination of k numbers 
(no matter the order) among a given seq list of objects'''

def combinlist(seq, k):
    p = []
    i, imax = 0, 2**len(seq)-1
    while i<=imax:
        s = []
        j, jmax = 0, len(seq)-1
        while j<=jmax:
            if (i>>j)&1==1:
                s.append(seq[j])
            j += 1
        if len(s)==k:
            p.append(tuple(s))
        i += 1
    return p


'''Takes a dataframe of clusters number (prediction) for a set of observation, 
and computes the ARI score between pairs of columns.
Two modes are available:
- first_vs_others=False: to check the initialisation stability.
The columns are obtains for n_columns iterations of the same model
with different initialisation
- first_vs_others=True: to compare the predictions obtained with the whole
dataset (first column) and predictions obtained with a sample
(the other columns)
Return a pd.Series of the ARI scores (values) for each pair of columns (index).
'''

from sklearn.metrics import adjusted_rand_score

def ARI_column_pairs(df_mult_ser_clust, first_vs_others=False, print_opt=True):

    n_columns = len(df_mult_ser_clust.columns)
    n_clust = df_mult_ser_clust.stack().nunique()
    
    # Computes ARI scores for each pair of models
    ARI_scores = []
    if first_vs_others: # first columns versus the others
        pairs_list = [[df_mult_ser_clust.columns[0],
                       df_mult_ser_clust.columns[i]] \
                      for i in range(1, n_columns)]
        if print_opt: print("--- ARI between first and the {} others ---"\
                            .format(n_columns-1))
        name = f'ARI_{str(n_clust)}_clust_first_vs_others'
    else: # all pairs
        pairs_list = combinlist(df_mult_ser_clust.columns,2)
        if print_opt: print("--- ARI all {} unique pairs ---"\
                            .format(len(pairs_list)))
        name = f'ARI_{str(n_clust)}_clust_all_pairs'

    for i, j in pairs_list:
        ARI_scores.append(adjusted_rand_score(df_mult_ser_clust.loc[:,i],
                                              df_mult_ser_clust.loc[:,j]))

    # Compute the mean and standard deviation of ARI scores
    ARI_mean, ARI_std = np.mean(ARI_scores), np.std(ARI_scores)
    ARI_min, ARI_max = np.min(ARI_scores), np.max(ARI_scores)
    if print_opt: print("ARI: mean={:.3f}, std={:.3f}, min={:.3f}, max={:.3f} "\
            .format(ARI_mean, ARI_std, ARI_min, ARI_max))

    return pd.Series(ARI_scores, index=pd.Index(pairs_list),
                     name=name)


''' Builds a customizable column_transformer which parameters can be optimized in a GridSearchCV
CATEGORICAL : three differents startegies for 3 different types of
categorical variables:
- low cardinality: customizable strategy (strat_low_card)
- high cardinality: customizable strategy (strat_high_card)
- boolean or equivalent (2 categories): ordinal
QUANTITATIVE (remainder): 
- StandardScaler

-> EXAMPLE (to use apart from gscv):
cust_enc = CustTransformer(thresh_card=12,
                       strat_binary = 'ord',
                       strat_low_card = 'ohe',
                       strat_high_card = 'loo',
                       strat_quant = 'stand')
cust_enc.fit(X_tr, y1_tr)
cust_enc.transform(X_tr).shape, X_tr.shape

-> EXAMPLE (to fetch names of the modified dataframe):
small_df = df[['Outlier', 'Neighborhood', 'CertifiedPreviousYear',
               'NumberofFloors','ExtsurfVolRatio']]
# small_df.head(2)
cust_trans = CustTransformer()
cust_trans.fit(small_df)
df_enc = cust_trans.transform(small_df)
cust_trans.get_feature_names(small_df)

'''
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import category_encoders as ce
from sklearn.preprocessing import *
import numpy as np
import pandas as pd


class CustTransformer(BaseEstimator):

    def __init__(self, thresh_card=12,
                 strat_binary='ord', strat_low_card='ohe',
                 strat_high_card='bin', strat_quant='stand'):
        self.thresh_card = thresh_card
        self.strat_binary = strat_binary
        self.strat_low_card = strat_low_card
        self.strat_high_card = strat_high_card
        self.strat_quant = strat_quant
        self.dict_enc_strat = {'binary': strat_binary,
                               'low_card': strat_low_card,
                               'high_card': strat_high_card,
                               'numeric': strat_quant}

    def d_type_col(self, X):
        bin_cols = (X.nunique()[X.nunique() <= 2].index)
        X_C_cols = X.select_dtypes(include=['object', 'category'])
        C_l_card_cols = \
            X_C_cols.nunique()[X_C_cols.nunique() \
                .between(3, self.thresh_card)].index
        C_h_card_cols = \
            X_C_cols.nunique()[X_C_cols.nunique() > self.thresh_card].index
        Q_cols = [c for c in X.select_dtypes(include=[np.number]).columns \
                  if c not in bin_cols]
        d_t = {'binary': bin_cols,
               'low_card': C_l_card_cols,
               'high_card': C_h_card_cols,
               'numeric': Q_cols}
        d_t = {k: v for k, v in d_t.items() if len(v)}
        # print(d_t)
        return d_t

    def get_feature_names(self, X, y=None):
        if self.has_num and self.has_cat:
            self.ct_cat.fit(X, y)
            cols = self.ct_cat.get_feature_names() + self.num_cols
        elif self.has_num and not self.has_cat:
            cols = self.num_cols
        elif not self.has_num and self.has_cat:
            self.ct_cat.fit(X, y)
            cols = self.ct_cat.get_feature_names()
        else:
            cols = None
        return cols

    def fit(self, X, y=None):
        # Dictionary to translate strategies
        d_enc = {'ohe': ce.OneHotEncoder(),
                 'hash': ce.HashingEncoder(),
                 'ord': ce.OrdinalEncoder(),
                 'loo': ce.LeaveOneOutEncoder(),
                 'bin': ce.BinaryEncoder(),
                 'stand': StandardScaler(),
                 'minmax': MinMaxScaler(),
                 'maxabs': MaxAbsScaler(),
                 'robust': RobustScaler(quantile_range=(25, 75)),
                 'norm': Normalizer(),
                 'quant_uni': QuantileTransformer(output_distribution='uniform'),
                 'quant_norm': QuantileTransformer(output_distribution='normal'),
                 'boxcox': PowerTransformer(method='box-cox'),
                 'yeo': PowerTransformer(method='yeo-johnson'),
                 'log': FunctionTransformer(func=lambda x: np.log1p(x),
                                            inverse_func=lambda x: np.expm1(x)),
                 'none': FunctionTransformer(func=lambda x: x,
                                             inverse_func=lambda x: x),
                 }

        # # dictionnaire liste des transfo categorielles EXISTANTES
        d_t = self.d_type_col(X)
        # numerics
        self.has_num = ('numeric' in d_t.keys())
        # categoricals
        self.has_cat = len([s for s in d_t.keys() if s in ['binary', 'low_card', 'high_card']]) > 0
        if self.has_cat:
            list_trans = []  # dictionnaire des transfo categorielles EXISTANTES
            for k, v in d_t.items():
                if k != 'numeric':
                    list_trans.append((k, d_enc[self.dict_enc_strat[k]], v))

            self.cat_cols = []  # liste des colonnes catégorielles à transformer
            for k, v in self.d_type_col(X).items():
                if k != 'numeric': self.cat_cols += (list(v))

            self.ct_cat = ColumnTransformer(list_trans)
            self.cat_trans = Pipeline([("categ", self.ct_cat)])

        if self.has_num:
            self.num_trans = Pipeline([("numeric", d_enc[self.strat_quant])])
            self.num_cols = d_t['numeric']

        if self.has_num and self.has_cat:
            self.column_trans = \
                ColumnTransformer([('cat', self.cat_trans, self.cat_cols),
                                   ('num', self.num_trans, self.num_cols)])
        elif self.has_num and not self.has_cat:
            self.column_trans = \
                ColumnTransformer([('num', self.num_trans, self.num_cols)])
        elif not self.has_num and self.has_cat:
            self.column_trans = ColumnTransformer([('cat', self.cat_trans, self.cat_cols)])
        else:
            print("The dataframe is empty : no transformation can be done")

        return self.column_trans.fit(X, y)

    # OLD VERSION WITHOUT NAME OF THE COLUMNS, OUTPUT AS A NP.ARRAY
    # def transform(self, X, y=None): 
    #     return  self.column_trans.transform(X)
    # def fit_transform(self, X, y=None):
    #     if y is None:
    #         self.fit(X)
    #         return self.column_trans.transform(X)
    #     else:
    #         self.fit(X, y)
    #         return self.column_trans.transform(X)

    def transform(self, X, y=None):  # to get a dataframe
        return pd.DataFrame(self.column_trans.transform(X),
                            index=X.index,
                            columns=self.get_feature_names(X, y))

    def fit_transform(self, X, y=None):
        if y is None:
            self.fit(X)
            return pd.DataFrame(self.column_trans.transform(X),
                                index=X.index,
                                columns=self.get_feature_names(X, y))
        else:
            self.fit(X, y)
            return pd.DataFrame(self.column_trans.transform(X, y),
                                index=X.index,
                                columns=self.get_feature_names(X, y))



'''
Takes two series giving for each row :
- the true label
- the cluster label
Then computes the matrix counting each pair of true category/ cluster label.
Then reorder the lines and columns in order to have maximum diagonal.
The best bijective correspondance between categories and clusters is obtained by
 list(zip(result.columns, result.index))
'''

from sklearn.preprocessing import FunctionTransformer
from scipy.optimize import linear_sum_assignment

def confusion_matrix_clust(true_cat, clust_lab, normalize=False,
                           margins_sums=False, margins_score=False):

from sklearn.preprocessing import FunctionTransformer
from scipy.optimize import linear_sum_assignment

def conf_matr_max_diago(true_cat, clust_lab, normalize=False):

    ### Count the number of articles in eact categ/clust pair
    cross_tab = pd.crosstab(true_cat, clust_lab,
                            normalize=normalize)

    ### Rearrange the lines and columns to maximize the diagonal values sum
    # Take the invert values in the matrix
    func = lambda x: 1/(x+0.0000001)
    inv_func = lambda x: (1/x) - 0.0000001
    funct_trans = FunctionTransformer(func, inv_func)
    inv_df = funct_trans.fit_transform(cross_tab)

    # Use hungarian algo to find ind and row order that minimizes inverse
    # of the diag vals -> max diag vals
    row_ind, col_ind = linear_sum_assignment(inv_df.values)
    inv_df = inv_df.loc[inv_df.index[row_ind],
                        inv_df.columns[col_ind]]

    # Take once again inverse to go back to original values
    cross_tab = funct_trans.inverse_transform(inv_df)
    result = cross_tab.copy(deep='True')

    if normalize == False:
        result = result.round(0).astype(int)

    return result

'''
Function that takes a pd.Series of labels (same number of different labels
in each column) and attribute a harmonized set of names to all the columns.
The names are chosen in order to maximize the diagonal of a confusion matrix
made on true-categories and each column.
NB: if no true_category series is given, the first columns is considered 
as the true_category series.  
'''

def categ_identificator(df_labels, true_cat=None):

    # takes the first columns as true category if true_cat not specified
    if true_cat is None:
        true_cat_ser = df_labels.iloc[:,0]
        df_labels = df_labels.iloc[:,1:]
    else:
        true_cat_ser = true_cat

    df_ = pd.DataFrame()

    # loop on all the lists of labels
    for col in df_labels.columns:
        # generate a confusion matrix that maximizes the diagonal
        cm = conf_matr_max_diago(true_cat_ser, df_labels[col],
                                normalize=False)
        # generate a translation dictionary to apply to the column col
        transl = dict(zip(cm.columns, cm.index))
        df_[col] = df_labels[col].map(transl)

    # if true_cat was the first columns, reinsert
    if true_cat is None:
        df_.insert(0, true_cat_ser.name, true_cat_ser)
    return df_


def plot_conf_matrix_cat_vs_clust(true_cat, clust_lab, normalize=False,
                                  margins_sums=False, margins_score=False):

    result = conf_matr_max_diago(true_cat, clust_lab, normalize=normalize)

    if margins_sums:
        # assign the sums margins to the result dataframe
        marg_sum_vert = result[result.columns].sum(1)
        result = result.assign(cat_sum=marg_sum_vert)
        marg_sum_hor = result.loc[result.index].sum(0)
        result = result.append(pd.Series(marg_sum_hor,
                                         index=result.columns,
                                         name='clust_sum'))

    if margins_score:
        # Compute a correpondance score between clusters and categories
        li_cat_clust = list(zip(cross_tab.index,
                                cross_tab.columns))
        li_cat_corresp_score, li_clust_corresp_score = [], []
        for i, tup in enumerate(li_cat_clust):
            match = result.loc[tup]
            cat_corr_score = 100*match/cross_tab.sum(1).iloc[i]
            clust_corr_score = 100*match/cross_tab.sum(0).iloc[i]
            li_cat_corresp_score.append(cat_corr_score)
            li_clust_corresp_score.append(clust_corr_score)

        # assign the margins to the result dataframe
        if margins_sums:
            li_cat_corresp_score.append('-')
            li_clust_corresp_score.append('-')

        marg_vert = pd.Series(li_cat_corresp_score,
                              index=result.index,
                              name='cat_matching_score_pct')
        result = result.assign(cat_matching_score_pct=marg_vert) 

        marg_hor = pd.Series(li_clust_corresp_score + ['-'],
                             index=result.columns,
                             name='clust_matching_score_pct')
        result = result.append(marg_hor)

    result = result.fillna('-')

    return result

    '''
Computing the trustworthiness category by category
'''
from sklearn.manifold import trustworthiness

def groups_trustworthiness(df, df_proj, ser_clust, n_neighbors=5):
    
    gb_clust = df.groupby(ser_clust)
    tw_clust, li_clust = [], []
    for n_clust, ind_sub_df in gb_clust.groups.items():
        li_clust.append(n_clust)
        tw_clust.append(trustworthiness(df.loc[ind_sub_df],
                                        df_proj.loc[ind_sub_df],
                                        n_neighbors=n_neighbors, metric='euclidean'))
    ser = pd.Series(tw_clust,
                    index=li_clust,
                    name='tw')
    return ser

''' Plots the points on two axis (projection choice available : PCA, UMAP, t-SNE)
with clusters coloring if model available (grey if no model given).
NB: if the model wa already fitted, does not refit.'''

import seaborn as sns
from sklearn.manifold import trustworthiness
from sklearn.preprocessing import LabelEncoder

def plot_projection_cat_clust(df, model=None, ser_clust = None, true_cat=None,
                              proj='PCA', tw_n_neigh=5, title=None, figsize=(5, 3),
                              size=1, edgelinesize=25, centersize=150,
                              palette='tab10', legend_on=False,
                              bboxtoanchor=None, fig=None, ax=None,
                              random_state=14):

    fig = plt.figure(figsize=figsize) if fig is None else fig
    ax = fig.add_subplot(111) if ax is None else ax

    # a1 - if model : computes clusters, clusters centers and plot with colors
    if model is not None:

        # Computes the axes for projection with centers
        # (uses fitted model if already fitted)
        dict_proj, dict_proj_centers, model = prepare_2D_axes(df,
                                                              proj=[proj],
                                                              model=model,
                                                              centers_on=True,
                                                              random_state=random_state)

        # ...or using model already fitted in prepare_2D_axes to get it
        #### all clusterers don't have .predict/labels_ method -> changed
        if hasattr(model, 'labels_'):
            clust = model.labels_
        else:
            clust = model.predict(df)
        ser_clust = pd.Series(clust,
                              index=df.index,
                              name='Clust')
        
    # a2 - if no model but ser_clust is given, plot with colors
    elif ser_clust is not None:
        
        # Computes the axes for projection
        dict_proj, dict_proj_centers, _ = \
            prepare_2D_axes(df, ser_clust=ser_clust, proj=[proj],
                            model=None, centers_on=True,
                            random_state=random_state)
            
    # Computing the global trustworthiness
    trustw = trustworthiness(df, dict_proj[proj],
                             n_neighbors=tw_n_neigh, metric='euclidean')
    # Computing the trustworthiness category by category
    ser_tw_cat = groups_trustworthiness(df, dict_proj[proj], true_cat,
                                        n_neighbors=tw_n_neigh)
    ser_tw_clust = groups_trustworthiness(df, dict_proj[proj], ser_clust,
                                          n_neighbors=tw_n_neigh)

    # b1 - if ser_clust exists (either calculated from model or given)
    if ser_clust is not None:
        # Prepare the correpondance between categories and clusters
        cm = conf_matr_max_diago(true_cat,ser_clust)
        cat_list = cm.index # liste des catégories, dans l'ordre
        clust_list = cm.columns # liste des clusters, dans l'ordre

        # prepare color values
        n_clust = ser_clust.nunique()
        c1 = sns.color_palette(palette, cm.shape[0]).as_hex() # cat
        c2 = sns.color_palette(palette, cm.shape[1]).as_hex() # clust
        colors1 = true_cat.map(dict(zip(cat_list, c1))) # traduit une catégorie en couleur de c1
        colors2 = ser_clust.map(dict(zip(clust_list, c2))) # traduit un cluster en couleur de c2

        # # prepare markers values
        # lenc = LabelEncoder()
        # markers = pd.Series([f'${i}$' for i in lenc.fit_transform(true_cat)],
        #                     index=true_cat.index)
        # Plot the data points
        for i in range(len(ser_clust.index)):
            ax.scatter(dict_proj[proj].iloc[i, 0],
                        dict_proj[proj].iloc[i, 1],
                        color=colors1.iloc[i],
                        s=size, linewidths=edgelinesize,
                        alpha=1, #marker=markers[i],
                        ec=colors2.iloc[i])

        # calculation of centers
        cent_clust_df = dict_proj[proj].assign(clust=ser_clust)\
                        .groupby(ser_clust).mean()         
        cent_cat_df = dict_proj[proj].assign(cat=true_cat)\
                        .groupby(true_cat).mean()
        
        # categories centers
        for i, name_cat, col in zip(range(len(cat_list)), cat_list, c1):
            # Showing the categories centers
            ax.scatter(cent_cat_df.iloc[:, 0].loc[name_cat],
                       cent_cat_df.iloc[:, 1].loc[name_cat],
                       marker='o', c=col, alpha=0.7, s=size,
                       edgecolor='lightgrey', linewidths=edgelinesize,
                       label="{}: {} | tw={:0.2f}".format(i, name_cat,
                                                          ser_tw_cat[name_cat]),
                       zorder=10) # for the labels only
            ax.scatter(cent_cat_df.iloc[:, 0].loc[name_cat],
                       cent_cat_df.iloc[:, 1].loc[name_cat],
                       marker='o', c=col, alpha=0.7, s=centersize,
                       edgecolor='k', zorder=10) # to plot the circle
            # Showing the categories centers labels (number)
            ax.scatter(cent_cat_df.iloc[:, 0].loc[name_cat],
                       cent_cat_df.iloc[:, 1].loc[name_cat],
                       marker=r"$ {} $".format(i+1),
                       c='k', alpha=1, s=70, zorder=100)
        
        # clusters centers
        for i, name_clust, col in zip(range(len(clust_list)), clust_list, c2):
            # Showing the clusters centers
            ax.scatter(cent_clust_df.iloc[:, 0].loc[name_clust],
                       cent_clust_df.iloc[:, 1].loc[name_clust],
                       marker='o', c='lightgrey', alpha=0.7, s=size,
                       edgecolor=col, linewidths=edgelinesize,
                       label="{}: {} | tw={:0.2f}".format(i, name_clust,
                                                          ser_tw_clust[name_clust]),
                       zorder=10) # for the labels only
            ax.scatter(cent_clust_df.iloc[:, 0].loc[name_clust],
                       cent_clust_df.iloc[:, 1].loc[name_clust],
                       marker='o', c=col, alpha=0.7, s=centersize,
                       edgecolor='k', zorder=20) # to plot the circle
            # Showing the categories centers labels (number)
            ax.scatter(cent_clust_df.iloc[:, 0].loc[name_clust],
                       cent_clust_df.iloc[:, 1].loc[name_clust],
                       marker=r"$ {} $".format(i+1),
                       c='dimgrey', alpha=1, s=70, zorder=100)

        # link between the centers
        for n_cat, n_clust in zip(cat_list, clust_list):
            x1 = cent_cat_df.iloc[:,0].loc[n_cat]
            x2 = cent_clust_df.iloc[:,0].loc[n_clust]
            y1 = cent_cat_df.iloc[:,1].loc[n_cat]
            y2 = cent_clust_df.iloc[:,1].loc[n_clust]
            plt.plot([x1, x2], [y1, y2],
                     color='k', linewidth=1)

        if legend_on:
            plt.legend().get_frame().set_alpha(0.3)
            if bboxtoanchor is not None:
                plt.legend(bbox_to_anchor=bboxtoanchor)
            else: 
                plt.legend()

    # b2 - if no ser_clust: only plot points in grey
    else:
        # Computes the axes for projection without centers
        dict_proj = prepare_2D_axes(df,
                                    proj=[proj],
                                    centers_on=False,
                                    random_state=random_state)
        # Plotting the point in grey
        ax.scatter(dict_proj[proj].iloc[:, 0],
                   dict_proj[proj].iloc[:, 1],
                   s=size, alpha=0.7, c='dimgrey')

    title = "Projection: " + proj + "(trustworthiness: {:.2f})".format(trustw)\
             if title is None else title
    ax.set_title(title + "\n(trustworthiness: {:.2f})".format(trustw),
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('ax 1'), ax.set_ylabel('ax 2')



'''
Takes a confusion matrix (best if diagonal maximized) with true categories as
indices and clusters as columns (can be obtained using the function
'confusion_matrix_clust', which ensures the diagonal values are maximum i.e.
the best bijective correponding cat-clut pairs have been found),
then plot the sankey confusion matrix.
Use the option static to plot a static image of the original interactive graph.

NB: the code below needs to be run if you are on colab

    # in order to get orca to be installed in colab (to display static plotly graphs)
    !pip install plotly>=4.0.0
    !wget https://github.com/plotly/orca/releases/download/v1.2.1/orca-1.2.1-x86_64.AppImage -O /usr/local/bin/orca
    !chmod +x /usr/local/bin/orca
    !apt-get install xvfb libgtk2.0-0 libgconf-2-4
'''

import plotly.graph_objects as go
from IPython.display import Image

def plot_sankey_confusion_mat(cm, static=False, figsize=(2, 1.7),
                              font_size=14, scale=1, palette = 'tab10'):

    n_cat = cm.shape[0]
    n_clust = cm.shape[1]
    source = np.array([n_clust*[i] for i in range(n_cat)]).ravel()
    target = np.array([[i] for i in range(n_cat,n_clust+n_cat)]*n_cat).ravel()
    value = cm.values.ravel()
    nodes_lab = list(cm.index)+list(cm.columns)
    alpha_nodes, alpha_links = 0.7, 0.3
    my_pal = sns.color_palette(palette, max(cm.shape))
    pal_nodes_cat = list([f'rgba({r},{g},{b},{alpha_nodes})' \
                        for r, g, b in my_pal[:n_cat]])
    pal_nodes_clust = list([f'rgba({r},{g},{b},{alpha_nodes})' \
                            for r, g, b in my_pal[:n_clust]])
    nodes_colors = (pal_nodes_cat + pal_nodes_clust)#.as_hex()

    pal_links = list([f'rgba({r},{g},{b},{alpha_links})' for r, g, b in my_pal[:n_cat]])
    dict_links_colors = dict(zip(range(n_cat), pal_links))
    links_colors = np.vectorize(dict_links_colors.__getitem__)(source)#.as_hex()

    # Prepare the graph
    fig = go.Figure(data=[go.Sankey(node = dict(pad = 15,
                                                thickness = 20,
                                                line = dict(color = "black",
                                                            width = 0.5),
                                                label = nodes_lab,
                                                color = nodes_colors),
                                    link = dict(source = source,
                                                target = target,
                                                value = value,
                                                # label = ,
                                                color = links_colors,
                                                ))])
    # title
    fig.update_layout(title_text="Sankey confusion diagram | \
true categories vs. clusters", font_size=font_size)
    if static:
        w, h = figsize
        img_bytes = fig.to_image(format="png", width=w, height=h, scale=scale)
        # Image(img_bytes)
        return img_bytes
    else:
        fig.show()

''' from a sentence, containing words (document):
- tokenizes the words if only composed of alphanumerical data,
- removes stopwords if list is given (stopwords)
- stems the words if stemmer given
NB: This pre-processing function can be used to prepare data for Word2Vec
'''
from nltk.stem.snowball import EnglishStemmer
import spacy
import nltk
nltk.download('averaged_perceptron_tagger')

def tokenize_clean(document, stopwords=None, keep_tags=None, # ('NN' or 'JJ')
                   lemmatizer=None, stemmer=None):
    # 1 - tokenizing the words in each description
    tokenizer = nltk.RegexpTokenizer(r'[A-Za-z]+')
    li_words = tokenizer.tokenize(document)
    # 2 - lower case
    li_words = [s.lower() for s in li_words]
    # 3 - keep only certain tags
    if keep_tags is not None:
        li_words = [word for word,tag in nltk.pos_tag(li_words)\
            if tag in keep_tags]
    if stopwords is None: stopwords=[]
    # 4 - lemmatizing or stemming
    if lemmatizer is not None:
        lem_doc = lemmatizer(' '.join(li_words))
        li_words = [token.lemma_ for token in lem_doc]
    elif stemmer is not None:
        li_words = [stemmer.stem(s) for s in li_words]
    # 5 - removing stopwords
    li_words = [s for s in li_words if s not in stopwords]

    return li_words

    ''' Takes a pd.Series containing the texts of each description
applies a preprocessing function if given (stopwords, stemming...)
then turn the descriptions in vectors (bow of tf-idf, depending on the avlue of
 tfidf_on)
 returns document term matrix as a dataframe and the list of new excluded words.
'''

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

def compute_doc_terms_df(ser_desc, 
                         preproc_func=None,
                         preproc_func_params=None,
                         vec_params=None,
                         tfidf_on=False,
                         print_opt=False):

    # ---- Apply a stemming of lemmatization prior to vectorization
    if preproc_func is not None:
        ser_desc = ser_desc.apply(lambda x: preproc_func(x,
                                                         **preproc_func_params))
        ser_desc = ser_desc.apply(lambda x: ' '.join(x))
    else:
        ser_desc = ser_desc
    
    # ---- Vectorization of each of the texts (row)
    if tfidf_on:
        # TF-IDF matrix
        vec = TfidfVectorizer(**vec_params)
    else:
        # BOW matrix (count)
        vec = CountVectorizer(**vec_params)

    doc_term = vec.fit_transform(ser_desc)
    if print_opt:
        print( "Created %d X %d doc_term matrix" % (doc_term.shape[0],
                                                    doc_term.shape[1]))

    # ---- Vocabulary of the document_term matrix
    doc_term_voc = vec.get_feature_names()
    if print_opt:
        print("Vocabulary has %d distinct terms" % len(doc_term_voc))

    # ---- Get the list of the new stop-words
    new_sw = vec.stop_words_
    if print_opt:
        print("Old stop-words list has %d entries" % len(sw) )
        print("New stop-words list has %d entries" % len(new_sw))

    doc_term_df = pd.DataFrame(doc_term.todense(),
                index=ser_desc.index, # each item
                columns=doc_term_voc) # each word

    # document term matrix as a dataframe and the list of new excluded words
    return doc_term_df, new_sw


'''
Takes a vectorized matrix (dataframe) of the documents
(Document-trem matrix: BOW or tf-idf... documents(rows) x words (columns))
and returns the projected vectors in the form of a dataframe
(words (rows) x w2v dimensions(columns))
'''

def proj_term_doc_on_w2v(term_doc_df, w2v_model, print_opt=False):

    # Checking the number of words of our corpus existing in the wiki2vec dictionary
    li_common_words = []
    for word in term_doc_df.columns:
        word_ = w2v_model.get_word(word)
        if word_ is not None:
            li_common_words.append(word)
    if print_opt:
        print(f"The w2v dictionary contains {len(li_common_words)} words out of \
the {term_doc_df.shape[1]} existing in our descriptions,\ni.e. \
{round(100*len(li_common_words)/term_doc_df.shape[1],1)}% of the whole vocabulary.")

    # extracting each of the word vectors
    word_vectors_df = pd.DataFrame()
    for word in li_common_words:
        word_vectors_df[word] = w2v_model.get_word_vector(word)
    word_vectors_df = word_vectors_df.T
    word_vectors_df.columns = ['dim_'+str(i)\
                               for i in range(word_vectors_df.shape[1])]

    # projection of the Document_terms matrix on the wiki2vec
    w2v_emb_df = term_doc_df[li_common_words].dot(word_vectors_df)

    return w2v_emb_df


''' Builds a customizable NLP column_transformer which parameters
can be optimized in a GridSearchClust
'''
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
# from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import *
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.snowball import EnglishStemmer
import spacy
import nltk
nltk.download('averaged_perceptron_tagger')

import numpy as np
import pandas as pd
from wikipedia2vec import Wikipedia2Vec

from wikipedia2vec import Wikipedia2Vec

class CustNLPTransformer(BaseEstimator, TransformerMixin):

    def __init__(self, stopwords=None, keep_tags=None, stemmer=None,
                 lemmatizer=None, min_df=0, max_df=1.0, max_features=None,
                 tfidf_on=False, ngram_range=(1,1), binary=False,
                 w2v=None, pname_weight=0.5):
        
        self.stopwords = stopwords
        self.keep_tags = keep_tags
        self.lemmatizer = lemmatizer
        self.stemmer = stemmer
        self.min_df = min_df
        self.max_df = max_df
        self.max_features = max_features
        self.tfidf_on = tfidf_on
        self.ngram_range = ngram_range
        self.binary = binary
        self.w2v = w2v
        self.pname_weight = pname_weight
        self.preproc_func_params={'stopwords': self.stopwords,
                                  'keep_tags': self.keep_tags,
                                  'lemmatizer': self.lemmatizer,
                                  'stemmer': self.stemmer}
        self.vec_params = {'min_df': self.min_df,
                           'max_df': self.max_df,
                           'max_features': self.max_features,
                           'ngram_range': self.ngram_range,
                           'binary': self.binary}


        # all preprocessing params to None (faster)
        if set([v for k, v in self.preproc_func_params.items()]) == set([None]):
            self.preproc_func = None
        else: # else tokenize_clean private function will be called
            self.preproc_func = self.__tokenize_clean

    # "private" method to prepropcess data inside '__compute_doc_terms_df'

    def __tokenize_clean(self, document, stopwords=None, keep_tags=None, # ('NN','JJ')
                    lemmatizer=None, stemmer=None):
        
        # 1 - tokenizing the words in each description
        tokenizer = nltk.RegexpTokenizer(r'[A-Za-z]+')
        li_words = tokenizer.tokenize(document)
        # 2 - lower case
        li_words = [s.lower() for s in li_words]
        # 3 - keep only certain tags
        if keep_tags is not None:
            li_words = [word for word,tag in nltk.pos_tag(li_words)\
                if tag in keep_tags]
        if stopwords is None: stopwords=[]
        # 4 - lemmatizing or stemming
        if lemmatizer is not None:
            lem_doc = lemmatizer(' '.join(li_words))
            li_words = [token.lemma_ for token in lem_doc]
        elif stemmer is not None:
            li_words = [stemmer.stem(s) for s in li_words]
        # 5 - removing stopwords
        li_words = [s for s in li_words if s not in stopwords]

        return li_words


    # "private" method to be used to apply transformation and get a df
    def __compute_doc_terms_df(self, ser_desc, preproc_func=None,
                               preproc_func_params=None, vec_params=None,
                               tfidf_on=None, vec=None):
        # ---- Apply a stemming or lemmatization prior to vectorization
        if preproc_func is not None:
            ser_desc = ser_desc.apply(lambda x: \
                                      preproc_func(x, **preproc_func_params))
            ser_desc = ser_desc.apply(lambda x: ' '.join(x))
        else:
            ser_desc = ser_desc
        # ---- Vectorization of each of the texts (row)
        if vec is None: # if no trained vectorized given
            if tfidf_on:
                # TF-IDF matrix
                vec = TfidfVectorizer(**vec_params)
            else:
                # BOW matrix (count)
                vec = CountVectorizer(**vec_params)
            vec.fit(ser_desc)
        else: # if a vectorizer is given
            try: # test if it is already fitted
                check_is_fitted(vec, attributes=None, all_or_any='any')
            except NotFittedError as e:
                vec.fit(ser_desc)
                print("Warning: 'vec' was not fitted -> has been fitted with 'df_desc'")
        doc_term = vec.transform(ser_desc)
        # ---- Vocabulary of the document_term matrix
        doc_term_voc = vec.get_feature_names()
        # # ---- Get the list of the new stop-words
        # new_sw = vec.stop_words_
        doc_term_df = pd.DataFrame(doc_term.todense(),
                                   index=ser_desc.index, # each item
                                   columns=doc_term_voc) # each word
        # document term matrix as a dataframe and the fitted vectorizer
        return doc_term_df, vec

    def fit(self, X, y=None):
        # nothing to fit - only set dictionaries (if a set_params had been run...)
        self.preproc_func_params={'stopwords': self.stopwords,
                                  'keep_tags': self.keep_tags,
                                  'lemmatizer': self.lemmatizer,
                                  'stemmer': self.stemmer}
        self.vec_params = {'min_df': self.min_df,
                           'max_df': self.max_df,
                           'max_features': self.max_features,
                           'ngram_range': self.ngram_range,
                           'binary': self.binary}
        return self

    def transform(self, X, y=None):  # returns a dataframe

        # X must be splitted in two parts : X_desc and X_pname
        X_desc, X_pname = X.iloc[:, 0], X.iloc[:, 1]

        # tranformation of X_pname into a custom BOW
        df_pname_trans, vec_fitted = self.__compute_doc_terms_df(\
                     ser_desc=X_pname,
                     preproc_func=self.preproc_func, 
                     preproc_func_params=self.preproc_func_params,
                     vec_params=self.vec_params,
                     tfidf_on=self.tfidf_on,
                     vec=None) # vec not fitted yet

        # tranformation of X_desc into a custom BOW (vec fitted with desc)
        df_desc_trans, _ = self.__compute_doc_terms_df(\
                     ser_desc=X_desc,
                     preproc_func=self.preproc_func,
                     preproc_func_params=self.preproc_func_params,
                     vec=vec_fitted) # vec fitted on the descriptions
        
        # Mix the X_desc and X_pname BOWs into one BOW (weight)

        df_trans = (df_desc_trans.mul(1-self.pname_weight,
                                      fill_value=0))\
                    .add(df_pname_trans.mul(self.pname_weight,
                                            fill_value=0),
                        fill_value=0)
        # if word_embedding is enabled, projection of the BOW on a given w2v
        if self.w2v:
            wiki2vec = Wikipedia2Vec.load("../DATA/enwiki_20180420_100d.pkl")
            df_trans = proj_term_doc_on_w2v(df_trans, wiki2vec,
                                            print_opt=False)
        return df_trans

    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X, y)

''' Builds a topics modeler which parameters (model, number of topics)
can be optimized in a GridSearchClust.
.transform: returns the DOCUMENTS/TOPICS matrix
.predict: returns the list of the most probable topic for each document
NB: takes a dataframe as X.
'''
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import *
from sklearn.decomposition import NMF
from sklearn.decomposition import LatentDirichletAllocation as LDA
from sklearn.decomposition import TruncatedSVD
import numpy as np
import pandas as pd

class TopicsModeler(BaseEstimator):

    def __init__(self, n_model='nmf', n_components=7, random_state=None):#, model_params):

        self.n_model = n_model
        self.n_components = n_components
        self.random_state = random_state
        # self.model_params = model_param

        # Model name -> object
        self.dict_models = {'lsa': TruncatedSVD(),
                            'nmf': NMF(init="nndsvd"),
                            'lda': LDA()}

        # Instantiate the model
        try:
            self.model = self.dict_models[self.n_model]#.set_params(*self.model_params)
        except:
            print(f"ERROR: {self.n_model} is an unknown topics modeliser. \n\
Please, choose between 'nmf', 'lda' and 'lsa'")

    def fit(self, X, y=None):

        # Re-Instantiate the model
        try:
            self.model = self.dict_models[self.n_model]#.set_params(*self.model_params)
        except:
            print(f"ERROR: {self.n_model} unknown topics modeliser. \n\
Please, choose between 'nmf', 'lda' and 'lsa'")

        # Set the parameters
        self.model.set_params(n_components = self.n_components,
                              random_state = self.random_state)

        # Fit the model
        self.model.fit(X)

        return self

    def __compute_DOC_TOP_matrix(self, X, y=None): # DOCUMENTS/TOPICS Matrix
    # actualization of n_components
        self.n_components = self.model.transform(X.values).shape[1]
        self.W = pd.DataFrame(self.model.transform(X.values),
                              index=X.index, # documents
                              columns=['topic_'+str(i)\
                                       for i in range(1,self.n_components+1)]) # topics

    def __compute_TOP_WORDS_matrix(self, X, y=None): # TOPICS/WORDS Matrix

        self.H = pd.DataFrame(self.model.components_, 
                              index=['topic_'+str(i)\
                                     for i in range(1,self.n_components+1)], # topics
                              columns=X.columns) # words

    def transform(self, X, y=None):  # to get the df of the DOC/TOPICS matrix

        self.__compute_DOC_TOP_matrix(X)
        self.__compute_TOP_WORDS_matrix(X)

        # Converting topics scores to best cluster label (higher val column)
        ser_res = self.W.idxmax(1)

        return self.W

    def predict(self, X, y=None):  # to get a ser of the best label

        self.__compute_DOC_TOP_matrix(X)
        self.__compute_TOP_WORDS_matrix(X)

        # Converting topics scores to best cluster label (higher val column)
        ser_res = self.W.idxmax(1)

        return ser_res

    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X, y)

    def fit_predict(self, X, y=None):
        self.fit(X, y)
        return self.predict(X, y)


'''
Class to optimize clustering score.
Instantiate with a clusterer (estimator), a grid parameter (param_grid)
and a scoring function or a dict of scores (scoring) to be translated
in actual scores (see the compute_score)
'''


import numpy as np
import pandas as pd
import copy
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import ParameterGrid
from collections import defaultdict
from sklearn.metrics import silhouette_score, calinski_harabasz_score,\
 davies_bouldin_score, adjusted_mutual_info_score, adjusted_rand_score,\
 homogeneity_score, completeness_score, v_measure_score


class GridSearchClust(BaseEstimator, TransformerMixin):

    def __init__(self, estimator, param_grid_estim, #param_grid_preproc=None,
                 scoring=None, scoring_true_lab=None, refit='silh',
                 greater_is_better=True, return_estimators=True):

        # Get the parameters
        self.estimator = estimator
        self.param_grid_estim = param_grid_estim
        # self.param_grid_preproc = param_grid_preproc
        self.scoring = scoring
        self.scoring_true_lab = scoring_true_lab
        self.refit = refit
        self.greater_is_better = greater_is_better
        self.return_estimators = return_estimators

    def __compute_score(self, X, clust_lab, n_score):

        dict_scores = {
            # Scores related to the clusters labels found by our estimator
               'silh': silhouette_score(X, clust_lab),
               'cal-har': calinski_harabasz_score(X, clust_lab),
               'dav_bould': davies_bouldin_score(X, clust_lab),
            # Scores comparing true labels and clusters found by our estimator
               'ami': adjusted_mutual_info_score(self.scoring_true_lab, clust_lab),
               'ari': adjusted_rand_score(self.scoring_true_lab, clust_lab),
               'homog': homogeneity_score(self.scoring_true_lab, clust_lab),
               'complet': completeness_score(self.scoring_true_lab, clust_lab),
               'v_meas': v_measure_score(self.scoring_true_lab, clust_lab),
               }
        return dict_scores[n_score]

    # Generates a dataframe of all the models tested, their scores and parameters
    def __results_to_df(self):

        gsc_res = self.results_
        df_gsc = pd.DataFrame()
        for k, v in gsc_res.items():
            if k == 'scores': # dict de listes : scores (que des nbes OK)
                df_ = pd.DataFrame(v)
                # li_scores = df_.columns
            elif k =='params': # liste de dicts : params
                df_ = pd.DataFrame(v)
                li_params = df_.columns
            else: # liste d'objets (estimators) ou de nombres (refit_score)
                df_ = pd.DataFrame(v, columns=[k])
            # concatène les colonnes
            df_gsc = pd.concat([df_gsc, df_], axis=1)
        return df_gsc

    # Fills None or np.nan values in a dataframe accordingly to the type
    # of the column:'None' string if the column type is 'object' np.nan otherwise
    def __selective_null_filler(self, df):

        obj_cols = df.select_dtypes(include=['object']).columns
        num_cols = df.select_dtypes(include=[np.number]).columns
        values = dict([(col, 'None') if col in obj_cols else (col, np.nan) \
                                                            for col in df])
        return df.fillna(value=values)

    # Find best parameters for a given score
    def __get_best_params(self, n_score):

        df_ = self.__results_to_df()
        li_params = pd.DataFrame(self.results_['params']).columns
        # concatenate the .results in a dataframe and fills None values
        df_fillna = self.__selective_null_filler(self.__results_to_df())
        # find best params (filled values) for the given score
        best_index = df_fillna[n_score].idxmax()
        best_params = df_fillna.loc[best_index].loc[li_params] # best params with nan filled
        return best_params, best_index, df_fillna

    # Find best estimator for a given score
    def __get_best_estimator(self, n_score):

        _, best_index, df_fillna = self.__get_best_params(n_score)
        return df_fillna.loc[best_index]['estimators']

    def fit(self, X, verbose=False):

        # Initialize the dict of results
        self.results_ = {"scores": {},
                         "params": [],
                         "estimators": [],
                        #  "fit_times": [],
                         "refit_score": []}

        # Iterate upon all combinations of parameters
        estim_score = defaultdict(list)
        nb_params = len(list(ParameterGrid(self.param_grid_estim)))

        for i, param in enumerate(ParameterGrid(self.param_grid_estim),1):

            if verbose: print('\r', f"{i}/{nb_params}:", end='')

            # Change the parameters of the estimator
            self.estimator = self.estimator.set_params(**param)

            # If the estimator is a pipe,
            if hasattr(self.estimator, 'steps'): # if estimator is a pipeline
                pipe_wo_last_estim = Pipeline(self.estimator.steps[0:-1])
                last_estim = self.estimator[-1] # .steps[-1][1]
                # compute the first steps separately
                X_trans = pipe_wo_last_estim.fit_transform(X)
                # fit the last estimator
                last_estim.fit(X_trans)
                # compute the labels
                labels = last_estim.predict(X_trans)
            else:
                X_trans = X
                # fit the model
                self.estimator.fit(X_trans)
                # compute the labels
                labels = self.estimator.predict(X_trans)

            # Compute the refit score
            try:
                refit_score = self.__compute_score(X_trans, labels,
                                                   self.refit)
            except:
                print('ERREUR calcul refit_score: is scoring_true_lab correctly set ?')
                refit_score = np.nan
            # Other scores (scoring)
            if not self.scoring:  # if scoring parameter is/are not defined
                estim_score['score'] = \
                    {'ari(default)': self.__compute_score(X_trans, labels,
                                                          'ari')}
            else:  # If scoring parameter is/are defined
                if type(self.scoring) not in (tuple, list):
                    self.scoring = [self.scoring]
                else:
                    # looping over each score in the scoring list
                    for n_sco in self.scoring:
                        try:
                            estim_score[n_sco] = estim_score[n_sco] + \
                                [self.__compute_score(X_trans, labels, n_sco)]
                        except:
                            estim_score[n_sco] = estim_score[n_sco] + [np.nan]
                            print("ERROR: score computation hasn't worked")

            # # Measure training time while fitting the model on the data
            # time_train = %timeit -n1 -r1 -o -q self.estimator.fit(X)
            # time_train = time_train.average

            # saving results, parameters and models in a dict
            self.results_["refit_score"].append(refit_score)  # refit score
            self.results_["params"].append(param)  # parameters
            if self.return_estimators:
                model_trans = copy.deepcopy(self.estimator)
                self.results_["estimators"].append(model_trans)  # trained models
            # self.results_["fit_times"].append(time_train)  # training time

        self.results_["scores"] = dict(estim_score)  # dict of lists of scores
        self.results_["refit_score"] = np.array(self.results_["refit_score"])
  
        # Selecting best model based on the refit_score
        # -----------------------------------
        # initialisation
        best_estim_index, best_score = None, None  
        # iterating over scores
        for index, score in enumerate(self.results_["refit_score"]):

            # initialisation
            if not best_score:
                best_score = score
                best_estim_index = index

            # if score is better than current best_score
            cond = score > best_score if self.greater_is_better\
                                                 else score < best_score
            if cond:
                    # update the current best_score and current best_estim_index
                    best_score = score
                    best_estim_index = index
        
        # Update attributes of the instance
        self.best_score_ = self.results_["refit_score"][best_estim_index]
        self.best_params_ = self.results_["params"][best_estim_index]
        if self.return_estimators:
            self.best_estimator_ = self.results_["estimators"][best_estim_index]
        self.best_index_ = best_estim_index
        # self.refit_time_ = self.results_["fit_times"][best_estim_index]

        # refit the best model
        if self.return_estimators:
            self.best_estimator_.fit(X)
        
        return self


# NB: The transform method will return the dataframe just before the clustering

    def transform(self, X, y=None, optim_score=None):

        if optim_score is None:
            best_model = self.best_estimator_
        else:
            best_model = self.__get_best_estimator(optim_score)

        # If the estimator is a pipe,
        if hasattr(best_model, 'steps'): # if estimator is a pipeline
            best_pipe_wo_last_estim = Pipeline(best_model.steps[0:-1])
            # compute the first steps separately
            X_trans = best_pipe_wo_last_estim.fit_transform(X)
            # fit the last estimator
        else:
            print("No multistep pipeline: returned only the original dataframe...")
            X_trans = X
       
        return X_trans

    def predict(self, X, y=None, optim_score=None):

        if optim_score is None:
            best_model = self.best_estimator_
        else:
            best_model = self.__get_best_estimator(optim_score)

        # use the .predict method of the best estimator on the best model
        return best_model.predict(X)


'''Takes a dataframe of clusters number (prediction) for a set of observation, 
and computes the ARI score between pairs of columns.
Two modes are available:
- first_vs_others=False: to check the initialisation stability.
The columns are obtains for n_columns iterations of the same model
with different initialisation
- first_vs_others=True: to compare the predictions obtained with the whole
dataset (first column) and predictions obtained with a sample
(the other columns)
Return a pd.Series of the ARI scores (values) for each pair of columns (index).
'''

from sklearn.metrics import adjusted_rand_score

def comp_clust_metrics_col_pairs(df_mult_ser_clust, n_score='ari',
                                 first_vs_others=False, print_opt=True):
    
    def cat_clust_score(col1, col2, n_score='ari'):
        dict_scores = {'ami': adjusted_mutual_info_score(col1, col2),
                       'ari': adjusted_rand_score(col1, col2),
                       'homog': homogeneity_score(col1, col2),
                       'complet': completeness_score(col1, col2),
                       'v_meas': v_measure_score(col1, col2)}
        return dict_scores[n_score]

    n_columns = len(df_mult_ser_clust.columns)
    n_clust = df_mult_ser_clust.nunique().mean()
    if n_clust != df_mult_ser_clust.nunique().median():
        print("ERROR: all the columns don't have the same number of clusters")
        return None
    
    # Computes chosen category/clusters comparing scores for each pair of models
    clust_scores = []
    if first_vs_others: # first columns versus the others
        pairs_list = [(df_mult_ser_clust.columns[0],
                       df_mult_ser_clust.columns[i]) for i in range(1, n_columns)]
        if print_opt: print("--- {} between first\
 and the {} others ---".format(n_score, n_columns-1))
        name = f'{n_score}_{str(n_clust)}_1st_vs_others'
    else: # all pairs
        pairs_list = combinlist(df_mult_ser_clust.columns,2)
        if print_opt: print(f"--- {n_score} all {len(pairs_list)} \
unique pairs ---")
        name = f'{n_score}_{str(n_clust)}_all_pairs'

    for i, j in pairs_list:
        clust_scores.append(cat_clust_score(df_mult_ser_clust.loc[:,i],
                                            df_mult_ser_clust.loc[:,j],
                                            n_score = n_score))

    # Compute the mean and standard deviation of category/clusters scores
    clust_sc_mean, clust_sc_std = np.mean(clust_scores), np.std(clust_scores)
    clust_sc_min, clust_sc_max = np.min(clust_scores), np.max(clust_scores)
    if print_opt: print("{}: mean={:.3f}, std={:.3f}, min={:.3f}, max={:.3f} "\
                        .format(n_score, clust_sc_mean, clust_sc_std,
                                 clust_sc_min, clust_sc_max))

    return pd.Series(np.array(clust_scores), index=pairs_list, name=name)

''' Transformer that translates all the non numeric values into strings
(including None) in a dict or a dataframe (column wise)
'''
import numbers
# si contient des None, alors convertir tous les objects en string

def object_none_translater(dict_or_df):
    if type(dict_or_df) == dict:
        # Change any non numeric value to string
        dict_or_df_transl = {k: v if isinstance(v, numbers.Number) else str(v)\
                             for k,v in dict_or_df.items()}
    elif type(dict_or_df) == pd.core.frame.DataFrame:
        # Change None to str (so the type of any None-containing col becomes 'object')
        dict_or_df_transl = dict_or_df.fillna('None')
        # Convert the content of all object columns to strings
        cols = dict_or_df_transl.select_dtypes('object').columns
        dict_or_df_transl[cols] = dict_or_df_transl[cols].applymap(lambda x: str(x))
    else:
        print("ERROR: you passed an object to 'object_none_translater'\
 that is neither a dict nor a pd.DataFrame")
    return dict_or_df_transl



'''
Generates a dataframe of all the models tested, their scores and parameters
'''
def results_to_df(gsc):

    df_gsc = pd.DataFrame()
    for k, v in gsc.results_.items():
        if k == 'scores': # dict de listes : scores (que des nbes OK)
            df_ = pd.DataFrame(v)
            # li_scores = df_.columns
        elif k =='params': # liste de dicts : params
            df_ = pd.DataFrame(v)
            li_params = df_.columns
        else: # liste d'objets (estimators) ou de nombres (refit_score)
            df_ = pd.DataFrame(v, columns=[k])
        # concatène les colonnes
        df_gsc = pd.concat([df_gsc, df_], axis=1)
    # df_gsc_transl = object_none_translater(df_gsc)
    return df_gsc

'''
Fills None or np.nan values in a dataframe accordingly to the type
of the column:
'None' string if the column type is 'object'
np.nan otherwise
'''

def selective_null_filler(df):
    obj_cols = df.select_dtypes(include=['object']).columns
    num_cols = df.select_dtypes(include=[np.number]).columns
    values = dict([(col, 'None') if col in obj_cols else (col, np.nan) \
                                                        for col in df])
    return df.fillna(value=values)

'''
Find best parameters for a given score
'''
def get_best_params(gsc, n_score=None):
    n_score = gsc.refit if n_score is None else n_score
    gsc_res = gsc.results_
    df_ = results_to_df(gsc)
    li_params = pd.DataFrame(gsc_res['params']).columns
    # concatenate the .results in a dataframe and fills None values
    df_fillna = selective_null_filler(results_to_df(gsc))
    # find best params (filled values) for the given score
    best_index = df_fillna[n_score].idxmax()
    best_params = df_fillna.loc[best_index].loc[li_params] # best params with nan filled
    return best_params, best_index, df_fillna


'''
Find best estimator for a given score
'''

def get_best_estimator(gsc, n_score):
    _, best_index, df_fillna = get_best_params(gsc, n_score)
    return df_fillna.loc[best_index]['estimators']

'''
From a fitted gsc (GridSearchClust) object and a param, returns
a sub dataframe of all the scores as a function of one chosen parameter (param)
NB: all other parameters are set to the values in best_params.
''' 
# fonction qui sort un dataframe partiel des résultats pour tous les scores,
# mais en fonction d'un seul paramètre

def filters_gsc_results(gsc, param, n_score=None):

    n_score = gsc.refit if n_score is None else n_score
    best_params, best_index, df_fillna = get_best_params(gsc, n_score)
    li_scores = gsc.results_['scores'].keys()
    df_filt = df_fillna.copy('deep')
    for par, val in best_params.iteritems():
        if par!= param:
            if type(val) == np.float64: # nan or float
                if not np.isnan(val): # not a nan (no more None in df_filt (=df_fillna))
                    df_filt = df_filt[df_filt[par]==val]
                else: # special filter for nan values among floats
                    df_filt = df_filt[df_filt[par].isna()]
            else: # string or object
                df_filt = df_filt[df_filt[par]==val]
    df_filt = df_filt.set_index(param)[li_scores]
    return df_filt

''' Plots a selection of scores (scores) or all the scores (scores=None)
obtained during the GridSearchClust as a collection of line graphs.
The other parameters (not plotted) are the parameters of the best estimator
(found by gridsearch). They're the same for all the line plot (contrary to
the 'plot_2Dgsclust_param_opt where other params may differ for each cell).
'''

def plot_gsc_multi_scores(gsc, param, title = None, x_log=False,
                          figsize = (12, 4), scores=None, optim_score=None):

    results = filters_gsc_results(gsc, param, optim_score)
    best_params, best_index, _ = get_best_params(gsc, optim_score)
    
    scoring = gsc.scoring if scores is None else scores

    fig, axs = plt.subplots(1,len(scoring))
    fig.set_size_inches(figsize)

    li_colors = ['b', 'r', 'g', 'purple', 'orange', 'brown', 'grey']
    if len(axs)==1 : axs = [axs]

    # Get the regular np array from the MaskedArray
        
    X_axis = np.array(results.index, dtype='float')

    for scorer, color, ax in zip(sorted(scoring), li_colors[:len(scoring)], axs):
        score = results[scorer].values
        
        df_ = pd.DataFrame({'param': X_axis,
                            'score': score,
                            }).sort_values(by='param')

        ax.plot(df_['param'], df_['score'], '-', marker='o', markersize=3,
            color=color, alpha=1)
        if x_log: ax.set_xscale('log')
        ax.set_title(scorer)

        y_min, y_max = ax.get_ylim()
        
        # Plot a dotted vertical line at the best score for that scorer marked by x
        best_score = results.loc[best_params[param], scorer]
        ax.plot([best_params[param], ] * 2, [y_min - abs(y_min)*0.1, best_score],
            linestyle='dotted', color=color, marker='x', markeredgewidth=3, ms=8)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel(param)
        ax.set_ylabel("Score")

        # Annotate the best score for that scorer
        len_str = len("{:.2f}".format(best_score))
        if best_params[param] < np.mean(X_axis):
            x_pos = best_params[param]*(1+0.015*len_str)
        else:
            x_pos = best_params[param]*(1-0.015*len_str)
        y_pos = best_score*1+(y_max-y_min)*0.05
        ax.annotate("{:0.2f}".format(best_score), 
                    (x_pos, y_pos),
                    color = color)  
    if title is not None:
        fig.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout(rect=(0,0,1,0.92))
    else:
        plt.tight_layout()
    plt.show()



''' Takes a GridSearchClust object and plots a heatmap of a chosen score (score)
against 2 chosen parameters.
NB: the score displayed for each cell is the one for the best other parameters.
'''

def plot_2D_gsclust_param_opt(gsc, params=None, score=None, fmt='.4g',
                           title=None, shorten_label=7, ax=None):

    ax = plt.subplot(1,1,1) if ax is None else ax

    score = 'refit_score' if score is None else score

    params_gsc = params

    _, _, _, df_res = filters_gsclust_results(gsc, params_gsc[0],
                                              return_df_res=True)
    max_scores = df_res.groupby(params_gsc).agg(lambda x: max(x))[score]
    sns.heatmap(max_scores.unstack(), annot=True, fmt=fmt, ax=ax)

    if shorten_label != False:
        thr = int(shorten_label)
        lab_x = [item.get_text() for item in ax.get_xticklabels()]
        short_lab_x = [s[:thr]+'...'+s[-thr:] if len(s)>thr else s for s in lab_x]
        ax.axes.set_xticklabels(short_lab_x)
        lab_y = [item.get_text() for item in ax.get_yticklabels()]
        short_lab_y = [s[:thr]+'...'+s[-thr:] if len(s)>thr else s for s in lab_y]
        ax.axes.set_yticklabels(short_lab_y)

    title = score if title is None else title
    ax.set_title(title)

# from sklearn.cluster import KMeans

# def clustering_doc_matrix(doc_matrix_df, name, n_clusters=7):
#     # Creating the Kmeans model
#     km = KMeans(n_clusters = n_clusters)
#     # Fitting the Kmeans model
#     km.fit(doc_matrix_df)
#     ser = pd.Series(km.labels_,
#                     index = doc_matrix_df.index,
#                     name = name)
#     return ser

# from sklearn.decomposition import NMF
# from sklearn.decomposition import LatentDirichletAllocation as LDA
# from sklearn.decomposition import TruncatedSVD

# def topicsmodeler_doc_matrix(doc_matrix_df, n_model, name, n_components=7):

#     dict_models = {'lsa': TruncatedSVD(),
#                    'nmf': NMF(init="nndsvd"),
#                    'lda': LDA()}
#     model = dict_models[n_model]

#     # Instantiation the topic modeler
#     model.set_params(n_components = n_components)

#     # Fitting the the topic modeler
#     model.fit(doc_matrix_df)

#     # DOCUMENTS/TOPICS Matrix
#     W = pd.DataFrame(model.fit_transform(doc_matrix_df.values),
#                      index=doc_matrix_df.index, # documents
#                      columns=['topic_'+str(i)\
#                               for i in range(1,n_components+1)]) # topics

#     # TOPICS/WORDS Matrix
#     H = pd.DataFrame(model.components_,
#                      index=['topic_'+str(i)\
#                             for i in range(1,n_components+1)], # topics
#                      columns=doc_matrix_df.columns) # words

#     # Converting topics scores to best cluster label (higher val column)
#     ser_res = pd.Series(W.idxmax(1),
#                         index = W.index,
#                         name = name)

#     return ser_res