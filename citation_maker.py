import streamlit as st
import requests

def get_bibtex_entry(item):
    authors = item.get("author", [])
    author_str = " and ".join([
        f"{a.get('family', '')}, {a.get('given', '')}" for a in authors
    ])
    year = item.get("issued", {}).get("date-parts", [[None]])[0][0]
    journal = item.get("container-title", [""])[0]
    volume = item.get("volume", "")
    issue = item.get("issue", "")
    
    # Get page or article number
    page = item.get("page")
    article_number = item.get("article-number") or item.get("article_number")
    
    # Filter out sketchy article_number = "1"
    if article_number == "1":
        article_number = None

    # Title and key
    title_str = item.get("title", [""])[0]
    bib_key = f"{authors[0]['family']}{year}" if authors and year else "citationKey"

    # Start building BibTeX
    bibtex_lines = [
        f"@article{{{bib_key},",
        f"  title = {{{title_str}}},",
        f"  author = {{{author_str}}},",
        f"  journal = {{{journal}}},",
    ]

    if volume:
        bibtex_lines.append(f"  volume = {{{volume}}},")

    if issue:
        bibtex_lines.append(f"  number = {{{issue}}},")

    if page:
        bibtex_lines.append(f"  pages = {{{page}}},")
    elif article_number:
        bibtex_lines.append(f"  pages = {{{article_number}}},")

    if year:
        bibtex_lines.append(f"  year = {{{year}}},")

    bibtex_lines.append("}")

    return "\n".join(bibtex_lines)

def search_papers(title, max_results=5):
    url = "https://api.crossref.org/works"
    params = {
        "query.title": title,
        "rows": max_results
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    items = data["message"]["items"]
    return items

# Streamlit app
st.title("BibTeX Citation Finder")
st.write("Enter a paper title to retrieve its citation in BibTeX format.")

title_input = st.text_input("Paper title:")

if title_input:
    with st.spinner("Searching..."):
        try:
            results = search_papers(title_input, max_results=5)

            if not results:
                st.warning("No results found.")
            else:
                # Let user choose among found titles
                titles = [item["title"][0] for item in results]
                selected_title = st.selectbox("Select the correct paper:", titles)

                selected_item = results[titles.index(selected_title)]
                bibtex_result = get_bibtex_entry(selected_item)
                st.code(bibtex_result, language="bibtex")

        except Exception as e:
            st.error(f"An error occurred: {e}")
