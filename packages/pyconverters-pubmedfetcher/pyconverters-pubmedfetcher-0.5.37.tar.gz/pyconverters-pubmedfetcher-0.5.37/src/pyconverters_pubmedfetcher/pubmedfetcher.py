import logging
import os
import re
import ssl
import xml.etree.ElementTree as ET
from enum import Enum
from functools import lru_cache
from typing import List, cast, Type

from blingfire import text_to_sentences_and_offsets
from metapub import PubMedFetcher, PubMedArticle
from metapub.exceptions import MetaPubError
from pydantic import Field, BaseModel
from pymultirole_plugins.v1.converter import ConverterParameters, ConverterBase
from pymultirole_plugins.v1.schema import Document, Sentence
from ratelimit import sleep_and_retry, limits
from starlette.datastructures import UploadFile
import metapub

import urllib.request
from lxml.etree import fromstring

_home = os.path.expanduser('~')
xdg_cache_home = os.environ.get('XDG_CACHE_HOME') or os.path.join(_home, '.cache')
NCBI_API_KEY = os.environ.get('NCBI_API_KEY')
DOI_REGEX = re.compile('^10.\\d{4,9}/[-._;()/:A-Z0-9]+$', flags=re.I)
PMID_REGEX = re.compile('^\\d{7,8}$', flags=re.I)
PMCID_REGEX = re.compile('^PMC\\d{6,8}$', flags=re.I)

# sending a doi to crossref (often) give you access to the document's information
CROSSREF_URL = "http://api.crossref.org/works/"
user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
headers = {'User-Agent': user_agent}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


class InputFormat(str, Enum):
    XML_PubmedArticleSet = 'XML PubmedArticleSet'
    ID_List = 'ID List'


class PubmedFetcherParameters(ConverterParameters):
    input_format: InputFormat = Field(InputFormat.XML_PubmedArticleSet, description="""Input format of the input file, among:<br/>
        <li>`XML PubmedArticleSet`: an XML file with PubmedArticleSet as root element.<br/>
        <li>`ID List`: A plain text file with a mix of Pubmed ids, PMC ids, DOIDs one by line.""")
    segment: bool = Field(True, description='Force fast sentence segmentation')


logger = logging.getLogger("pymultirole")


class PubmedFetcherConverter(ConverterBase):
    """PubmedFetcher converter .
    """

    def convert(self, source: UploadFile, parameters: ConverterParameters) \
            -> List[Document]:
        params: PubmedFetcherParameters = \
            cast(PubmedFetcherParameters, parameters)

        docs = []
        if params.input_format == InputFormat.ID_List:
            fetcher: PubMedFetcher = get_fetcher()
            inputs = source.file.readlines()
            for line in inputs:
                line = str(line, "utf-8") if isinstance(line, bytes) else line
                input = line.strip()
                try:
                    print("======================================================================")
                    print("convert: calling get_article(%s) ..." % input)
                    art = get_article(fetcher, input)
                    doc = None
                    if art is not None:
                        doc = article_to_document(art, params.segment)
                    if doc is not None:
                        docs.append(doc)
                except MetaPubError as e:
                    logger.exception(f"Cannot retrieve article with identifier {input}: {e}")
        elif params.input_format == InputFormat.XML_PubmedArticleSet:
            tree = ET.parse(source.file)
            for article in tree.iter('PubmedArticle'):
                art_xml = ET.tostring(article[0])
                art = PubMedArticle(art_xml)
                doc = article_to_document(art, params.segment)
                if doc is not None:
                    docs.append(doc)
        return docs

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return PubmedFetcherParameters


def article_to_document(art, segment=False):
    doc = None
    if art.title is not None or art.abstract is not None:
        art.title = art.title or ''
        art.abstract = art.abstract or ''
        metadata = {'journal': art.journal, 'year': art.year, 'types': list(art.publication_types.values()),
                    'authors': art.authors_str, 'url': art.url}
        if art.doi:
            metadata['doi'] = art.doi
        if art.pmc:
            metadata['pmc'] = art.pmc
        doc = Document(identifier=str(art.pmid), title=art.title, text=art.title + "\n\n" + art.abstract,
                       metadata=metadata,
                       annotations=[],
                       sentences=[])
        if segment:
            result = text_to_sentences_and_offsets(doc.text)
            if result:
                for start, end in result[1]:
                    doc.sentences.append(Sentence(start=start, end=end))
    return doc


@sleep_and_retry
@limits(calls=10, period=10)
def get_article(fetcher: PubMedFetcher, identifier: str) -> PubMedArticle:
    article: PubMedArticle = None
    success = 0
    if re.match(PMID_REGEX, identifier):
        article = fetcher.article_by_pmid(identifier)
    elif re.match(PMCID_REGEX, identifier):
        article = fetcher.article_by_pmcid(identifier)
    elif re.match(DOI_REGEX, identifier):
        # article = fetcher.article_by_doi(identifier)
        # first turn the doi into a pmid
        try:
            pmid = metapub.convert.doi2pmid(identifier)
            print("doi %s corresponds to pmid %s, retrieving ..." % (identifier, pmid))
            article = fetcher.article_by_pmid(pmid)
            success = 1
        except Exception as e:
            print("retrieving pmid for doi %s failed (%s), trying via crossref..." % (identifier, e))
        # pubmed could not translate the doi into pmid --> ask crossref
        if success == 0:
            try:
                url = CROSSREF_URL + identifier + ".xml"
                print("trying to retrieve article from %s..." % url)
                request = urllib.request.Request(url, None, headers)
                response = urllib.request.urlopen(request)
                data = response.read()
                with open("c:/tmp/test.xml", "w") as output:
                    output.write(str(data))
                tree = fromstring(data)

                abstract = '\n'.join(tree.xpath('.//jats:abstract', namespaces={'jats': 'http://www.ncbi.nlm.nih.gov/JATS1'})[0].itertext())

                article.abstract = abstract
                article.doi = identifier
                article.title = identifier  # '\n'.join(tree.xpath('.//journal_article/titles')[0].itertext())
                article.journal = "n.a."  # check later
                article.url = "n.a."  # check later
                article.year = "n.a."  # check later
                article.authors_str = "n.a."  # check later
                success = 1
            except Exception as e:
                print("error retrieving doi %s (%s)" % (identifier, e))
                return None
    else:
        raise MetaPubError(f"Unknown identifier pattern for {identifier}")
    if article.abstract is not None:
        print("abstact = %s" % article.abstract)
    return article


@lru_cache(maxsize=None)
def get_fetcher() -> PubMedFetcher:
    return PubMedFetcher()
