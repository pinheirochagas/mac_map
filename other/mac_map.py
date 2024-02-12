#%%
import requests
import xml.etree.ElementTree as ET
import networkx as nx
import matplotlib.pyplot as plt
import json
from fuzzywuzzy import process

#%%
def get_pmids(author):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    query = f"{author}[au]"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": 500  # Number of results to return
    }
    response = requests.get(base_url + "esearch.fcgi", params=params)
    root = ET.fromstring(response.content)
    pmids = [id_elem.text for id_elem in root.findall("IdList/Id")]
    return pmids

def get_paper_details(pmids):
    paper_details = []
    for pmid in pmids:
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml"
        }
        response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params=params)
        root = ET.fromstring(response.content)
        paper_info = {}

        # Fetching abstract
        abstract = root.find(".//Abstract/AbstractText")
        if abstract is not None:
            paper_info['abstract'] = abstract.text

        # Fetching authors
        authors = root.findall(".//AuthorList/Author")
        author_names = [author.find('LastName').text + " " + author.find('Initials').text for author in authors if author.find('LastName') is not None and author.find('Initials') is not None]
        paper_info['authors'] = author_names

        # Fetching publication year
        pub_year = root.find(".//PubDate/Year")
        if pub_year is not None:
            paper_info['year'] = pub_year.text

        # Fetching journal title
        journal = root.find(".//Journal/Title")
        if journal is not None:
            paper_info['journal'] = journal.text

        paper_details.append(paper_info)
    return paper_details

#%%

# Example usage
author = "Kristine Yaffe"
pmids = get_pmids(author)
papers = get_paper_details(pmids)
for paper in papers:
    print(paper)

# %%
faculty_list = [
    'Emily Paolillo', 'Pedro Pinheiro-Chagas', 'Boon Lead Tee', 'Claire Clelland',
    'Kaitlin Casaletto', 'Charles Windon', 'David Soleimani-Meigooni', 'Adam Staffaroni',
    'Joanna Hellmuth', 'Elena Tsoy', 'Lawren Vandevrede', 'Kristine Yaffe',
    'Paul Sampognaro', 'Lorenzo Pasquini', 'Maria Luisa Mandelli', 'Serggio Lanata',
    'Renaud La Joie', 'Salvatore Spina', 'Jessica de Leon', 'Katherine Rankin',
    'Christine Walsh', 'Jennifer Yokoyama', 'Mary De May', 'Lea Grinberg',
    'Kamalini Ranasinghe', 'Julio Rojas', 'Gil Rabinovici', 'David Perry',
    'Adam Boxer', 'Peter Ljubenkov', 'Melanie Stephens', 'Marilu Gorno Tempini',
    'Katherine Possin', 'Aimee Kao', 'Zachary Miller', 'Suzee Lee',
    'Winston Chiong', 'Michael Geschwind', 'Christa Pereira', 'Virginia Sturm',
    'Bill Seeley', 'Victor Valcour', 'Howie Rosen', 'Joel Kramer', 'Bruce Miller'
]


#%%
# Step 1: Gather Data
faculty_papers = {}
for faculty in faculty_list:
    pmids = get_pmids(faculty)  # Retrieve PMIDs for the normalized faculty name

    # Check if PMIDs are successfully retrieved
    if pmids:
        try:
            papers = get_paper_details(pmids)  # Get paper details for those PMIDs
            
            # Check if papers are successfully retrieved and are valid
            if papers:
                faculty_papers[faculty] = papers  # Store the papers under the original faculty name
            else:
                print(f"No valid paper details found for faculty: {faculty}")

        except ET.ParseError as e:
            print(f"XML parsing error for faculty {faculty}: {e}")
        except Exception as e:
            print(f"An error occurred while processing papers for faculty {faculty}: {e}")
    else:
        print(f"No PMIDs found for faculty: {faculty}")


#%% Check the output
for faculty, papers in faculty_papers.items():
    print(f"Faculty: {faculty}, Papers: {len(papers)}")

#%% load json file
with open('faculty_papers.json') as json_file:
    faculty_papers = json.load(json_file)

#%%
# get all the unique authors from the faculty papers
all_authors = set()
for faculty in faculty_papers:
    for paper in faculty_papers[faculty]:
        authors = paper.get('authors', [])
        for author in authors:
            all_authors.add(author)


#%%

def normalize_name(name):
    """ Normalize a name to lowercase. """
    return name.lower()

# Normalize faculty names
normalized_faculty = [normalize_name(name) for name in faculty_list]


# Fuzzy match and find the best match for each PubMed author in the faculty list
matches = {author: process.extractOne(normalize_name(author), normalized_faculty) for author in all_authors}

# Display the matches
for author, match in matches.items():
    print(f"PubMed author '{author}' matched with faculty '{match[0]}' with a score of {match[1]}")




#%%
# Specify the filename
filename = 'faculty_papers.json'

# Write to a file
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(faculty_papers, f, ensure_ascii=False, indent=4)


#%% Step 2: Build Co-Authorship Network
# Step 1: Build Co-Authorship Network
G = nx.Graph()

# Initialize node weights (number of connections) and edge weights (number of co-authorships)
node_weights = {faculty: 0 for faculty in faculty_papers}
edge_weights = {}

for faculty in faculty_papers:
    for paper in faculty_papers[faculty]:
        authors = paper.get('authors', [])
        for co_author in authors:
            if co_author in faculty_papers and co_author != faculty:
                G.add_edge(faculty, co_author)
                edge_weights[(faculty, co_author)] = edge_weights.get((faculty, co_author), 0) + 1
                node_weights[faculty] += 1
                node_weights[co_author] += 1

# Step 2: Visualize the Network
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G)  # positions for all nodes

# nodes
nx.draw_networkx_nodes(G, pos, node_size=[v * 100 for v in node_weights.values()])

# edges
for edge in G.edges():
    nx.draw_networkx_edges(G, pos, edgelist=[edge], width=edge_weights[edge])

# labels
nx.draw_networkx_labels(G, pos, font_size=10)

plt.title("Co-Authorship Network within Faculty")
plt.show()

# %%
from pyvis.network import Network
import networkx as nx

# Assuming you have a dictionary 'faculty_papers' mapping faculty names to their publication data

# Step 1: Build Co-Authorship Network
G = nx.Graph()

# Initialize node weights (number of connections) and edge weights (number of co-authorships)
node_weights = {faculty: 0 for faculty in faculty_papers}
edge_weights = {}

for faculty in faculty_papers:
    for paper in faculty_papers[faculty]:
        authors = paper.get('authors', [])
        for co_author in authors:
            if co_author in faculty_papers and co_author != faculty:
                G.add_edge(faculty, co_author)
                edge_weights[(faculty, co_author)] = edge_weights.get((faculty, co_author), 0) + 1
                node_weights[faculty] += 1
                node_weights[co_author] += 1

# Step 2: Create a Pyvis network
net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')

# Add nodes and edges to the Pyvis network
for node in G.nodes:
    net.add_node(node, size=node_weights[node]*10, title=node)

for edge in G.edges:
    net.add_edge(edge[0], edge[1], value=edge_weights[edge])

# Show the network
net.show('faculty_coauthorship_network.html')

# %%
# Sample faculty_papers dictionary (replace this with your actual data)
faculty_papers = {
    "Faculty1": [{"authors": ["Faculty1", "Faculty2"]}],
    "Faculty2": [{"authors": ["Faculty1", "Faculty2", "Faculty3"]}],
    "Faculty3": [{"authors": ["Faculty2", "Faculty3"]}]
}

# Initialize NetworkX Graph
G = nx.Graph()

# Add nodes and edges based on co-authorship
for faculty, papers in faculty_papers.items():
    G.add_node(faculty)  # Add faculty as node
    for paper in papers:
        for co_author in paper['authors']:
            if co_author in faculty_papers and co_author != faculty:
                G.add_edge(faculty, co_author)

# Check if nodes and edges have been added
print(f"NetworkX Graph | Nodes: {G.number_of_nodes()} | Edges: {G.number_of_edges()}")

# Initialize Pyvis Network from the NetworkX Graph
net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')
net.from_nx(G)

# Display the network
net.show('faculty_coauthorship_network.html')
# %%
